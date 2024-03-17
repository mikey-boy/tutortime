import hashlib

from tutortime.extensions import db
from tutortime.models import Image, Service, ServiceCategory, User

services = [
    [
        1,
        "Introduction to Psychology",
        "Explore the fundamental concepts of psychology, including behavior, cognition, and mental processes.",
        ServiceCategory.OTHER,
    ],
    [
        1,
        "World History: Ancient Civilizations",
        "Study ancient civilizations and their contributions to human history.",
        ServiceCategory.OTHER,
    ],
    [
        1,
        "Basic Physics Principles",
        "Understand fundamental principles of physics, including motion, forces, and energy.",
        ServiceCategory.OTHER,
    ],
    [
        1,
        "Introduction to Environmental Science",
        "Explore key concepts in environmental science, including ecosystems, biodiversity, and sustainability.",
        ServiceCategory.OTHER,
    ],
    [
        1,
        "Art Appreciation",
        "Learn about different art movements, styles, and famous artists throughout history.",
        ServiceCategory.OTHER,
    ],
    [
        2,
        "Introduction to Marketing",
        "Understand the basics of marketing, including market research, branding, and promotion strategies.",
        ServiceCategory.OTHER,
    ],
    [
        2,
        "Financial Literacy",
        "Gain essential knowledge about personal finance, budgeting, and investment basics.",
        ServiceCategory.OTHER,
    ],
    [
        2,
        "Business Ethics",
        "Explore ethical considerations in business decision-making and corporate responsibility.",
        ServiceCategory.OTHER,
    ],
    [
        2,
        "Entrepreneurship 101",
        "Learn the essentials of entrepreneurship, including business planning and startup strategies.",
        ServiceCategory.OTHER,
    ],
    [
        2,
        "Human Resource Management",
        "Understand key principles of human resource management in organizations.",
        ServiceCategory.OTHER,
    ],
    [
        3,
        "Introduction to Astronomy",
        "Explore the wonders of the universe, including planets, stars, and galaxies.",
        ServiceCategory.OTHER,
    ],
    [
        3,
        "Sociology: Understanding Society",
        "Study the structure and dynamics of human societies and social interactions.",
        ServiceCategory.OTHER,
    ],
    [
        3,
        "Introduction to Nutrition",
        "Learn about the principles of nutrition and the impact of diet on health.",
        ServiceCategory.WELLNESS,
    ],
    [
        3,
        "Introduction to Linguistics",
        "Explore the study of language, including its structure, meaning, and use.",
        ServiceCategory.OTHER,
    ],
    [
        3,
        "Creative Writing Workshop",
        "Develop your creative writing skills through various writing exercises and techniques.",
        ServiceCategory.OTHER,
    ],
    [
        4,
        "Introduction to Robotics",
        "Learn the basics of robotics, including robot design, programming, and applications.",
        ServiceCategory.OTHER,
    ],
    [
        4,
        "Digital Photography Basics",
        "Master the fundamentals of digital photography, including composition and editing techniques.",
        ServiceCategory.OTHER,
    ],
    [
        4,
        "Introduction to Political Science",
        "Explore the structure and functioning of political systems and institutions.",
        ServiceCategory.OTHER,
    ],
    [
        4,
        "Introduction to Public Speaking",
        "Develop effective public speaking skills for various situations and audiences.",
        ServiceCategory.OTHER,
    ],
    [
        4,
        "Health and Wellness Strategies",
        "Discover strategies for maintaining physical and mental well-being.",
        ServiceCategory.WELLNESS,
    ],
    [
        5,
        "Introduction to Python",
        "Learn the basics of Python programming language, including variables, data types, and control structures.",
        ServiceCategory.SOFTWARE,
    ],
    [
        5,
        "Web Development with Flask",
        "Build web applications using the Flask framework. Understand routing, templates, and database integration.",
        ServiceCategory.SOFTWARE,
    ],
    [
        5,
        "Data Analysis with Pandas",
        "Explore data manipulation and analysis using the Pandas library in Python.",
        ServiceCategory.SOFTWARE,
    ],
    [
        5,
        "Machine Learning Fundamentals",
        "Get started with machine learning concepts and algorithms. Includes hands-on exercises.",
        ServiceCategory.SOFTWARE,
    ],
    [
        5,
        "Database Design and SQL",
        "Learn database design principles and SQL for effective data storage and retrieval.",
        ServiceCategory.SOFTWARE,
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

    for service in services:
        service = Service(user_id=service[0], title=service[1], description=service[2], category=service[3])
        service.add()
        Image(service_id=service.id, category=service.category).add()
