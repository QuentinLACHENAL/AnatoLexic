AnatoLexic: Anatomy Revision Software

Video Demo: https://www.youtube.com/watch?v=9XINQWSVlQw


Project Overview
    AnatoLexic is an innovative educational software designed to revolutionize anatomy learning for students at the Higher Institute of Psychomotor Rehabilitation (ISRP) in Metz, France. Developed as a final project for the Harvard X CS50 Certificate, this interactive tool addresses the critical challenge of memorizing complex anatomical terminology through engaging and effective learning methods.

Motivation
    As an anatomy instructor, I recognized the significant difficulties students face when trying to memorize intricate anatomical terms. Traditional learning methods often prove challenging and demotivating, especially when dealing with complex medical terminology. AnatoLexic was conceived to transform this learning experience by making it more interactive, intuitive, and enjoyable.

Project structure (files and folders):

    Main Files
        main.py: Entry point that initializes the application and handles errors
        app.py: Core application class that manages the UI, word selection, flashcards, scoring, timers, and    Wikipedia image loading

    UI Components (/ui folder)
        theme_frame.py: Top frame for selecting anatomy themes and subthemes
        main_frame.py: Central frame displaying words, feedback, Wikipedia images, and action buttons
        advanced_frame.py: Controls for flashcard mode and letter suggestion
        bottom_frame.py: Score display, timer controls, and utility buttons

    Utilities (/utils folder)
        resource_utils.py: Handles file paths for both script and executable modes
        text_utils.py: Provides word scrambling while preserving punctuation
        wikipedia_utils.py: Fetches and displays images from Wikipedia

    Data
        words.py: Dictionary of all anatomical terminology organized by categories

Key Features
    Learning Modes
    AnatoLexic offers multiple innovative learning approaches to cater to different learning styles:

        Term Definition Guessing: Users are presented with a definition and must identify the correct anatomical term.
        Letter Unscrambling: Students unscramble letters to reveal the correct anatomical term.
        Definition-Term Matching: A challenging mode that tests comprehensive understanding by matching definitions to scrambled terms.

    Additional Supportive Features
    Visual Learning Support:

        Display of anatomical structures through static images and GIFs
        Visual representations to enhance understanding of complex anatomical concepts

    Research and Reference Tools:

        Direct links to relevant Wikipedia pages
        Curated YouTube video resources for supplementary learning
        Letter hints to assist with challenging terminology

    Learning Tracking:

        Study session timer
        Comprehensive progress statistics
        Performance tracking to monitor learning improvements

    Technical Considerations
        Language and Accessibility
        The current version of AnatoLexic is developed in French, specifically tailored to the needs of students at the ISRP. However, the project roadmap includes:

        Full English translation
        Potential expansion to other languages
        Increased international accessibility

    Development Approach
    The software was designed with a focus on:

        User-friendly interface
        Interactive learning experience
        Intuitive navigation
        Engaging educational technology

    Design Choices and Challenges
    Challenges Addressed

        Making complex anatomical terminology more approachable
        Creating an engaging learning interface
        Developing multiple interactive learning modes
        Implementing effective progress tracking

    Technical Decisions

        Chose Python for backend development due to its simplicity and robust libraries

    Future Roadmap
        Planned Enhancements

        Expand anatomical region coverage
        Develop additional exercise types
        Improve visualization capabilities
        Create English and potentially other language versions
        Implement more advanced progress tracking and personalized learning paths

    AI use
        I leveraged AI tools like ChatGPT and Claude throughout the development of AnatoLexic to understand complex topics such as the Wikipedia API for anatomy images and to help with coding and debugging.

        Though I began this project before starting CS50, it was initially basic and incomplete. I invested significant time to transform it into a fully functional educational tool for my students, adding features incrementally.

        This process revealed AI's limitations - despite excellent prompts, AI tools struggled to grasp the project's full scope. Managing these limitations while creating a comprehensive anatomy learning application proved to be an intense but educational experience.

Contact
Quentin LACHENAL

GitHub: QuentinLACHENAL

Developed with passion for improving anatomy education through technology.
