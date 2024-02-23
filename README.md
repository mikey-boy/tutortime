# tutortime.ca

Tutortime is an online time-bank platform focused on learning. Each user plays two roles on the platform:

- **As a teacher** you help other students in a subject you understand. You are awarded credits for your time
- **As a student** you can use your credits to schedule meetups with a teacher. They will help you learn about a subject you are interested in

Tutortime is a platform where users can learn new skills at no monetary cost.

## Setup

### Prerequisites

You will need the following installed:

- Python 3
- Pip

### Installation

```bash
# Clone the repository
git clone https://github.com/mikey-boy/tutortime.git
cd tutortime

# (Optional) Configure a virtual environment
# python -m venv .venv
# source .venv/bin/activate

# Install the Python dependencies
pip install -r requirements.txt

# Create a config file
cd tutortime
cp config-sample.py config.py

# Initialiaze the database with test data, run the app
flask initdb
flask run --debug
```

After the following steps the app should be available on [localhost](http://localhost:5000). OAuth2 integrations (Google, Facebook) will not work, but you should be able to create local user accounts.