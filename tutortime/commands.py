import hashlib

from tutortime.extensions import db
from tutortime.models import Service, ServiceCategory, User

services = [
    [
        "Introduction to Python",
        "Learn the basics of Python programming language, including variables, data types, and control structures.",
        ServiceCategory.SOFTWARE,
    ],
    [
        "Web Development with Flask",
        "Build web applications using the Flask framework. Understand routing, templates, and database integration.",
        ServiceCategory.SOFTWARE,
    ],
    [
        "Data Analysis with Pandas",
        "Explore data manipulation and analysis using the Pandas library in Python.",
        ServiceCategory.SOFTWARE,
    ],
    [
        "Machine Learning Fundamentals",
        "Get started with machine learning concepts and algorithms. Includes hands-on exercises.",
        ServiceCategory.SOFTWARE,
    ],
    [
        "Database Design and SQL",
        "Learn database design principles and SQL for effective data storage and retrieval.",
        ServiceCategory.SOFTWARE,
    ],
    [
        "Introduction to Psychology",
        "Explore the fundamental concepts of psychology, including behavior, cognition, and mental processes.",
        ServiceCategory.OTHER,
    ],
    [
        "World History: Ancient Civilizations",
        "Study ancient civilizations and their contributions to human history.",
        ServiceCategory.OTHER,
    ],
    [
        "Basic Physics Principles",
        "Understand fundamental principles of physics, including motion, forces, and energy.",
        ServiceCategory.OTHER,
    ],
    [
        "Introduction to Environmental Science",
        "Explore key concepts in environmental science, including ecosystems, biodiversity, and sustainability.",
        ServiceCategory.OTHER,
    ],
    [
        "Art Appreciation",
        "Learn about different art movements, styles, and famous artists throughout history.",
        ServiceCategory.OTHER,
    ],
    [
        "Introduction to Marketing",
        "Understand the basics of marketing, including market research, branding, and promotion strategies.",
        ServiceCategory.OTHER,
    ],
    [
        "Financial Literacy",
        "Gain essential knowledge about personal finance, budgeting, and investment basics.",
        ServiceCategory.OTHER,
    ],
    [
        "Business Ethics",
        "Explore ethical considerations in business decision-making and corporate responsibility.",
        ServiceCategory.OTHER,
    ],
    [
        "Entrepreneurship 101",
        "Learn the essentials of entrepreneurship, including business planning and startup strategies.",
        ServiceCategory.OTHER,
    ],
    [
        "Human Resource Management",
        "Understand key principles of human resource management in organizations.",
        ServiceCategory.OTHER,
    ],
    [
        "Introduction to Astronomy",
        "Explore the wonders of the universe, including planets, stars, and galaxies.",
        ServiceCategory.OTHER,
    ],
    [
        "Sociology: Understanding Society",
        "Study the structure and dynamics of human societies and social interactions.",
        ServiceCategory.OTHER,
    ],
    [
        "Introduction to Nutrition",
        "Learn about the principles of nutrition and the impact of diet on health.",
        ServiceCategory.WELLNESS,
    ],
    [
        "Introduction to Linguistics",
        "Explore the study of language, including its structure, meaning, and use.",
        ServiceCategory.OTHER,
    ],
    [
        "Creative Writing Workshop",
        "Develop your creative writing skills through various writing exercises and techniques.",
        ServiceCategory.OTHER,
    ],
    [
        "Introduction to Robotics",
        "Learn the basics of robotics, including robot design, programming, and applications.",
        ServiceCategory.OTHER,
    ],
    [
        "Digital Photography Basics",
        "Master the fundamentals of digital photography, including composition and editing techniques.",
        ServiceCategory.OTHER,
    ],
    [
        "Introduction to Political Science",
        "Explore the structure and functioning of political systems and institutions.",
        ServiceCategory.OTHER,
    ],
    [
        "Introduction to Public Speaking",
        "Develop effective public speaking skills for various situations and audiences.",
        ServiceCategory.OTHER,
    ],
    [
        "Health and Wellness Strategies",
        "Discover strategies for maintaining physical and mental well-being.",
        ServiceCategory.WELLNESS,
    ],
]


def clear_db():
    db.drop_all()
    db.create_all()


def initdb():
    clear_db()

    password = hashlib.sha256("password".encode()).hexdigest()
    mike = User(social_id="local$mike", username="mike", password=password, timezone="America/Toronto")
    dave = User(social_id="local$dave", username="dave", password=password, timezone="America/Toronto")
    fred = User(social_id="local$fred", username="fred", password=password, timezone="America/Toronto")
    pete = User(social_id="local$pete", username="pete", password=password, timezone="America/Toronto")
    alex = User(social_id="local$alex", username="alex", password=password, timezone="America/Toronto")
    paul = User(social_id="local$paul", username="paul", password=password, timezone="America/Toronto")

    mike.add()
    dave.add()
    fred.add()
    pete.add()
    alex.add()
    paul.add()

    i = 0
    for service in services:
        if i < 5:
            service = Service(
                user_id=mike.id, title=service[0], description=service[1], category=service[2], availability=0
            )
            service.add()
        elif i < 10:
            service = Service(
                user_id=dave.id, title=service[0], description=service[1], category=service[2], availability=0
            )
            service.add()
        elif i < 15:
            service = Service(
                user_id=fred.id, title=service[0], description=service[1], category=service[2], availability=0
            )
            service.add()
        elif i < 20:
            service = Service(
                user_id=pete.id, title=service[0], description=service[1], category=service[2], availability=0
            )
            service.add()
        elif i < 25:
            service = Service(
                user_id=alex.id, title=service[0], description=service[1], category=service[2], availability=0
            )
            service.add()
        else:
            service = Service(
                user_id=paul.id, title=service[0], description=service[1], category=service[2], availability=0
            )
            service.add()
        i += 1
