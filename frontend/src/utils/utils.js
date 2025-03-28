import dayjs from "dayjs";

export function parseDate(datetime) {
    if (datetime) {
        return dayjs(datetime).format("YYYY-MM-DD");
    }
}

export function parseTime(datetime) {
    if (datetime) {
        return dayjs(datetime).format("hh:mm A");
    }
}