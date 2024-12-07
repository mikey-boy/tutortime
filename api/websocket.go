package api

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/gorilla/websocket"
)

type Hub struct {
	// Registered clients.
	clients map[uint]*Client

	// Inbound messages from the clients.
	message chan Message

	// Register requests from the clients.
	register chan *Client

	// Unregister requests from clients.
	unregister chan *Client
}

// Client is a middleman between the websocket connection and the hub.
type Client struct {
	hub *Hub

	// The websocket connection.
	conn *websocket.Conn

	// The ID of the end user
	userID uint

	// Buffered channel of outbound messages.
	send chan Message
}

type apiMessage struct {
	RecieverID uint
	Message    string
	Lesson     struct {
		ServiceID uint
		LessonID  uint
		Title     string
		Date      string
		Time      string
		Duration  uint
	}
}

const (
	// Time allowed to write a message to the peer.
	writeWait = 10 * time.Second

	// Time allowed to read the next pong message from the peer.
	pongWait = 60 * time.Second

	// Send pings to peer with this period. Must be less than pongWait.
	pingPeriod = (pongWait * 9) / 10

	// Maximum message size allowed from peer.
	maxMessageSize = 512
)

var (
	newline = []byte{'\n'}
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
}

var hub Hub

// readMessage pumps messages from the websocket connection to the hub.
//
// The application runs readMessage in a per-connection goroutine. The application
// ensures that there is at most one reader on a connection by executing all
// reads from this goroutine.
func (client *Client) readMessage() {
	defer func() {
		client.hub.unregister <- client
		client.conn.Close()
	}()
	client.conn.SetReadLimit(maxMessageSize)
	client.conn.SetReadDeadline(time.Now().Add(pongWait))
	client.conn.SetPongHandler(func(string) error { client.conn.SetReadDeadline(time.Now().Add(pongWait)); return nil })
	for {
		_, reader, err := client.conn.NextReader()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("error: %v", err)
			}
			break
		}

		var apiMessage apiMessage
		json.NewDecoder(reader).Decode(&apiMessage)

		var message = Message{SenderID: client.userID, RecieverID: apiMessage.RecieverID, Message: apiMessage.Message}
		if apiMessage.Lesson.ServiceID != 0 || apiMessage.Lesson.LessonID != 0 {
			var service = Service{ID: apiMessage.Lesson.ServiceID}
			service.Get()

			var lesson = Lesson{ServiceID: apiMessage.Lesson.ServiceID, TutorID: service.UserID, Duration: apiMessage.Lesson.Duration}
			if service.UserID == message.SenderID {
				lesson.StudentID = message.RecieverID
				lesson.Status = ACCEPTED_TUTOR
			} else if service.UserID == message.RecieverID {
				lesson.StudentID = message.SenderID
				lesson.Status = ACCEPTED_STUDENT
			} else {
				continue
			}
			lesson.Datetime, err = time.Parse("2006-01-02 15:04:05", fmt.Sprintf("%s %s:00", apiMessage.Lesson.Date, apiMessage.Lesson.Time))
			if err != nil {
				fmt.Println(err)
			}

			message.Lesson = &lesson
		}

		message.Add()
		fmt.Printf("Message to read from client: '%+v'\n", message)

		client.hub.message <- message
	}
}

// writeMessage pumps messages from the hub to the websocket connection.
//
// A goroutine running writeMessage is started for each connection. The
// application ensures that there is at most one writer to a connection by
// executing all writes from this goroutine.
func (client *Client) writeMessage() {
	ticker := time.NewTicker(pingPeriod)
	defer func() {
		ticker.Stop()
		client.conn.Close()
	}()
	for {
		select {
		case message, ok := <-client.send:
			fmt.Printf("Message to write to client: '%s'\n", message.Message)
			client.conn.SetWriteDeadline(time.Now().Add(writeWait))
			if !ok {
				// The hub closed the channel.
				client.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			w, err := client.conn.NextWriter(websocket.TextMessage)
			if err != nil {
				return
			}
			bytes, _ := json.Marshal(message)
			w.Write(bytes)

			// Add queued chat messages to the current websocket message.
			n := len(client.send)
			for i := 0; i < n; i++ {
				w.Write(newline)
				message := <-client.send
				bytes, _ := json.Marshal(message)
				w.Write(bytes)
			}

			if err := w.Close(); err != nil {
				return
			}
		case <-ticker.C:
			client.conn.SetWriteDeadline(time.Now().Add(writeWait))
			if err := client.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

// serveWs handles websocket requests from the peer.
func ServeWs(writer http.ResponseWriter, request *http.Request) {
	user, ok := UserFromRequest(*request)
	if !ok {
		http.Error(writer, invalidSessionToken.String(), http.StatusUnauthorized)
		return
	}

	conn, err := upgrader.Upgrade(writer, request, nil)
	if err != nil {
		log.Println(err)
		return
	}

	client := &Client{hub: &hub, conn: conn, userID: user.ID, send: make(chan Message)}
	client.hub.register <- client
	fmt.Printf("Registered a new client for: %d\n", user.ID)

	// Allow collection of memory referenced by the caller by doing all work in
	// new goroutines.
	go client.writeMessage()
	go client.readMessage()
}

func CreateHub() {
	hub = Hub{
		message:    make(chan Message),
		register:   make(chan *Client),
		unregister: make(chan *Client),
		clients:    make(map[uint]*Client),
	}
}

func RunHub() {
	for {
		select {
		case client := <-hub.register:
			hub.clients[client.userID] = client
		case client := <-hub.unregister:
			if _, ok := hub.clients[client.userID]; ok {
				delete(hub.clients, client.userID)
				close(client.send)
			}
		case message := <-hub.message:
			if sender, ok := hub.clients[message.SenderID]; ok {
				select {
				case sender.send <- message:
				default:
					close(sender.send)
					delete(hub.clients, sender.userID)
				}
			}
			if reciever, ok := hub.clients[message.RecieverID]; ok {
				select {
				case reciever.send <- message:
				default:
					close(reciever.send)
					delete(hub.clients, reciever.userID)
				}
			}
		}
	}
}
