from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty, ColorProperty
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
import random
import json
from functools import partial

# Set window background color
Window.clearcolor = (0.95, 0.95, 0.95, 1)

class Question:
    """Class to hold question data"""
    def __init__(self, question, options, correct_index, language, explanation=""):
        self.question = question
        self.options = options
        self.correct_index = correct_index
        self.language = language
        self.explanation = explanation

class RoundedButton(Button):
    """Custom button with rounded corners"""
    button_color = ColorProperty([0.2, 0.6, 0.8, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self.color = (1, 1, 1, 1)
        self.font_size = '18sp'
        self.bold = False
        self.size_hint = (None, None)
        self.height = 50
        self.width = 200
        self.padding = (10, 10)
        
        with self.canvas.before:
            self.bg_color = Color(rgba=self.button_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            
        self.bind(pos=self.update_rect, size=self.update_rect, button_color=self.update_color)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
    def update_color(self, *args):
        self.bg_color.rgba = self.button_color
        
    def on_press(self):
        anim = Animation(button_color=[0.1, 0.4, 0.6, 1], duration=0.1)
        anim.start(self)
        Clock.schedule_once(self.reset_color, 0.1)
        
    def reset_color(self, dt):
        anim = Animation(button_color=[0.2, 0.6, 0.8, 1], duration=0.1)
        anim.start(self)

class LanguageButton(RoundedButton):
    """Custom button for language selection"""
    language = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = '20sp'
        self.bold = True
        self.size_hint = (0.8, 0.15)
        self.width = 300

class OptionButton(RoundedButton):
    """Custom button for answer options"""
    is_correct = BooleanProperty(False)
    index = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = 70
        self.width = 400
        self.markup = True
        self.button_color = [0.9, 0.9, 0.9, 1]
        self.color = (0.2, 0.2, 0.2, 1)
        
    def on_press(self):
        # Don't animate option buttons on press
        pass

class LanguageScreen(Screen):
    """Screen for selecting programming language"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        
        # Decorative header
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        title = Label(
            text='[b]Code Master[/b]',
            font_size='32sp',
            color=(0.2, 0.2, 0.2, 1),
            markup=True
        )
        subtitle = Label(
            text='Learn Programming Languages',
            font_size='20sp',
            color=(0.4, 0.4, 0.4, 1)
        )
        header.add_widget(title)
        header.add_widget(subtitle)
        main_layout.add_widget(header)
        
        # Language selection section
        selection_layout = BoxLayout(orientation='vertical', spacing=20, size_hint=(1, 0.5))
        
        select_label = Label(
            text='Choose a language to learn:',
            font_size='20sp',
            color=(0.4, 0.4, 0.4, 1),
            size_hint=(1, 0.2)
        )
        selection_layout.add_widget(select_label)
        
        # Language buttons
        btn_layout = BoxLayout(orientation='vertical', spacing=20, size_hint=(1, 0.8))
        
        languages = [
            ('Python', 'python'),
            ('JavaScript', 'js'),
            ('C++', 'cpp'),
            ('React', 'react')
        ]
        
        for lang_name, lang_code in languages:
            btn = LanguageButton(text=lang_name)
            btn.language = lang_code
            btn.bind(on_release=self.select_language)
            btn_layout.add_widget(btn)
            
        selection_layout.add_widget(btn_layout)
        main_layout.add_widget(selection_layout)
        
        # Footer
        footer = Label(
            text='Master programming concepts one question at a time',
            font_size='16sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, 0.2)
        )
        main_layout.add_widget(footer)
        
        self.add_widget(main_layout)
    
    def select_language(self, instance):
        self.manager.current_language = instance.language
        self.manager.current = 'quiz'

class QuizScreen(Screen):
    """Screen for displaying and answering quiz questions"""
    question_text = StringProperty('')
    score = NumericProperty(0)
    total_questions = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_question = None
        self.option_buttons = []
        self.questions_answered = 0
        self.max_questions = 10  # Number of questions per session
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header with score and back button
        header = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        self.back_btn = RoundedButton(
            text='← Back to Menu',
            size_hint=(0.3, 1)
        )
        self.back_btn.bind(on_release=self.go_back)
        header.add_widget(self.back_btn)
        
        self.score_label = Label(
            text='Score: 0/0',
            size_hint=(0.4, 1),
            color=(0.2, 0.2, 0.2, 1),
            font_size='18sp'
        )
        header.add_widget(self.score_label)
        
        self.language_label = Label(
            text='Python',
            size_hint=(0.3, 1),
            color=(0.2, 0.2, 0.2, 1),
            font_size='18sp',
            bold=True
        )
        header.add_widget(self.language_label)
        
        main_layout.add_widget(header)
        
        # Progress bar
        self.progress_layout = BoxLayout(size_hint=(1, 0.05), spacing=2)
        self.progress_bars = []
        main_layout.add_widget(self.progress_layout)
        
        # Question area
        question_container = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        question_container.add_widget(Label(
            text='Question:',
            size_hint=(1, 0.2),
            color=(0.3, 0.3, 0.3, 1),
            font_size='16sp'
        ))
        
        self.question_label = Label(
            text='Question will appear here',
            font_size='22sp',
            size_hint=(1, 0.8),
            color=(0.2, 0.2, 0.2, 1),
            text_size=(Window.width - 40, None),
            halign='center',
            valign='middle',
            markup=True
        )
        self.question_label.bind(size=self.question_label.setter('text_size'))
        question_container.add_widget(self.question_label)
        
        main_layout.add_widget(question_container)
        
        # Options area
        options_layout = GridLayout(cols=1, spacing=15, size_hint=(1, 0.55), padding=10)
        self.option_buttons = []
        
        for i in range(4):
            btn = OptionButton()
            btn.index = i
            btn.bind(on_release=self.check_answer)
            options_layout.add_widget(btn)
            self.option_buttons.append(btn)
            
        main_layout.add_widget(options_layout)
        
        self.add_widget(main_layout)
        
        # Result popup
        self.result_popup = ModalView(size_hint=(0.8, 0.6), background='', auto_dismiss=False)
        result_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.result_label = Label(
            font_size='24sp', 
            bold=True,
            size_hint=(1, 0.2)
        )
        result_layout.add_widget(self.result_label)
        
        self.explanation_label = Label(
            font_size='18sp',
            text_size=(Window.width * 0.7, None),
            halign='center',
            size_hint=(1, 0.5)
        )
        self.explanation_label.bind(size=self.explanation_label.setter('text_size'))
        result_layout.add_widget(self.explanation_label)
        
        # Next question button inside popup
        self.next_button = RoundedButton(
            text='Next Question',
            size_hint=(0.6, 0.2)
        )
        self.next_button.bind(on_release=self.next_question)
        
        button_container = BoxLayout(size_hint=(1, 0.3))
        button_container.add_widget(Label())  # Spacer
        button_container.add_widget(self.next_button)
        button_container.add_widget(Label())  # Spacer
        
        result_layout.add_widget(button_container)
        self.result_popup.add_widget(result_layout)
    
    def on_enter(self):
        self.questions_answered = 0
        self.score = 0
        self.total_questions = 0
        self.update_progress_bars()
        self.load_question()
        
    def update_progress_bars(self):
        self.progress_layout.clear_widgets()
        self.progress_bars = []
        
        for i in range(self.max_questions):
            bar = Label()
            bar.background_color = (0.8, 0.8, 0.8, 1)  # Light gray for unanswered
            self.progress_bars.append(bar)
            self.progress_layout.add_widget(bar)
    
    def update_progress(self, correct):
        if self.questions_answered - 1 < len(self.progress_bars):
            if correct:
                self.progress_bars[self.questions_answered - 1].background_color = (0.4, 0.8, 0.4, 1)  # Green for correct
            else:
                self.progress_bars[self.questions_answered - 1].background_color = (0.8, 0.4, 0.4, 1)  # Red for incorrect
        
    def load_question(self):
        language = self.manager.current_language
        self.language_label.text = language.upper()
        
        # Get a random question for the selected language
        questions = self.manager.questions[language]
        self.current_question = random.choice(questions)
        
        self.question_label.text = f'[b]{self.current_question.question}[/b]'
        
        # Set options
        for i, option in enumerate(self.current_question.options):
            self.option_buttons[i].text = option
            self.option_buttons[i].is_correct = (i == self.current_question.correct_index)
            self.option_buttons[i].button_color = [0.9, 0.9, 0.9, 1]
            self.option_buttons[i].disabled = False
    
    def check_answer(self, instance):
        # Disable all buttons to prevent multiple answers
        for btn in self.option_buttons:
            btn.disabled = True
            
        # Highlight the correct answer
        for i, btn in enumerate(self.option_buttons):
            if i == self.current_question.correct_index:
                btn.button_color = [0.4, 0.8, 0.4, 1]  # Green for correct
            
        if instance.index == self.current_question.correct_index:
            # Correct answer
            instance.button_color = [0.4, 0.8, 0.4, 1]  # Green
            self.show_result(True)
            self.score += 1
        else:
            # Wrong answer
            instance.button_color = [0.8, 0.4, 0.4, 1]  # Red
            self.show_result(False)
            
        self.total_questions += 1
        self.questions_answered += 1
        self.score_label.text = f'Score: {self.score}/{self.total_questions}'
        self.update_progress(instance.index == self.current_question.correct_index)
    
    def show_result(self, is_correct):
        if is_correct:
            self.result_label.text = 'Correct!'
            self.result_label.color = (0.2, 0.6, 0.2, 1)
        else:
            self.result_label.text = 'Incorrect!'
            self.result_label.color = (0.8, 0.2, 0.2, 1)
            
        self.explanation_label.text = self.current_question.explanation if self.current_question.explanation else "Keep learning!"
        self.result_popup.open()
    
    def next_question(self, instance):
        self.result_popup.dismiss()
        
        if self.questions_answered >= self.max_questions:
            self.show_final_score()
            return
            
        # Re-enable buttons for next question
        for btn in self.option_buttons:
            btn.disabled = False
            
        self.load_question()
    
    def show_final_score(self):
        self.result_popup.dismiss()
        
        final_view = ModalView(size_hint=(0.8, 0.6), background='')
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        score_label = Label(
            text=f'Final Score: {self.score}/{self.total_questions}',
            font_size='24sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1)
        )
        layout.add_widget(score_label)
        
        if self.score / self.total_questions >= 0.8:
            message = "Excellent! You've mastered this language!"
            color = (0.2, 0.6, 0.2, 1)
        elif self.score / self.total_questions >= 0.6:
            message = "Good job! Keep practicing!"
            color = (0.3, 0.5, 0.8, 1)
        else:
            message = "Keep learning! You'll improve with practice."
            color = (0.8, 0.4, 0.2, 1)
            
        message_label = Label(
            text=message,
            font_size='20sp',
            color=color
        )
        layout.add_widget(message_label)
        
        button_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)
        
        retry_btn = RoundedButton(text='Try Again')
        retry_btn.bind(on_release=lambda x: (final_view.dismiss(), self.restart_quiz()))
        button_layout.add_widget(retry_btn)
        
        menu_btn = RoundedButton(text='Back to Menu')
        menu_btn.bind(on_release=lambda x: (final_view.dismiss(), self.go_back(None)))
        button_layout.add_widget(menu_btn)
        
        layout.add_widget(button_layout)
        final_view.add_widget(layout)
        final_view.open()
    
    def restart_quiz(self):
        self.questions_answered = 0
        self.score = 0
        self.total_questions = 0
        self.update_progress_bars()
        self.load_question()
        
        # Re-enable buttons
        for btn in self.option_buttons:
            btn.disabled = False
    
    def go_back(self, instance):
        self.manager.current = 'language'

class LearningApp(App):
    def build(self):
        # Create screen manager
        sm = ScreenManager(transition=FadeTransition())
        sm.questions = self.load_questions()
        
        # Add screens
        sm.add_widget(LanguageScreen(name='language'))
        sm.add_widget(QuizScreen(name='quiz'))
        
        return sm
    
    def load_questions(self):
        # Sample questions for each language (100 questions each)
        # In a real app, you would load these from a file or database
        
        questions = {
            'python': [],
            'js': [],
            'cpp': [],
            'react': []
        }
        
        # Python questions
        python_questions = [
            ("Which keyword is used to define a function in Python?",
             ["func", "def", "function", "define"], 1,
             "The 'def' keyword is used to define functions in Python."),
            
            ("How do you create a comment in Python?",
             ["// comment", "/* comment */", "# comment", "-- comment"], 2,
             "Python uses the '#' symbol for single-line comments."),
            
            ("Which data type is mutable in Python?",
             ["tuple", "string", "list", "int"], 2,
             "Lists are mutable in Python, meaning they can be changed after creation."),
            
            ("What is the output of 'print(3 * 'hi')'?",
             ["hihihi", "3hi", "hi hi hi", "Error"], 0,
             "Multiplying a string by an integer repeats the string that many times."),
            
            ("Which method is used to remove an item from a list by value?",
             ["remove()", "delete()", "pop()", "discard()"], 0,
             "The remove() method removes the first occurrence of a value from a list."),
            
            ("How do you start a while loop in Python?",
             ["while condition:", "while (condition)", "while condition", "while: condition"], 0,
             "Python uses the syntax 'while condition:' with a colon at the end."),
            
            ("What is the correct way to create a class in Python?",
             ["class MyClass:", "class MyClass()", "class MyClass{}", "class MyClass[]"], 0,
             "Python class definitions use the 'class' keyword followed by the class name and a colon."),
            
            ("Which module is used for working with dates?",
             ["datetime", "time", "date", "calendar"], 0,
             "The datetime module provides classes for manipulating dates and times."),
            
            ("How do you open a file for reading in Python?",
             ["open('file.txt', 'r')", "open('file.txt', 'read')", "open('file.txt')", "read('file.txt')"], 0,
             "The open() function with 'r' mode is used to open a file for reading."),
            
            ("What does the 'self' parameter represent in a class method?",
             ["The class itself", "The instance of the class", "A reference to the superclass", "A reserved keyword"], 1,
             "'self' refers to the instance of the class and is used to access variables and methods."),
        ]
        
        # Add 90 more Python questions (in a real app, you'd have 100 total)
        for i in range(10, 100):
            questions['python'].append(Question(
                f"Python Question {i+1} - What is the result of {i} % 3?",
                [f"{i % 3}", f"{(i+1) % 3}", f"{(i+2) % 3}", f"{(i+3) % 3}"],
                0,
                "python",
                f"The modulus operator (%) returns the remainder of division. {i} divided by 3 has a remainder of {i % 3}."
            ))
        
        # Add the first 10 Python questions
        for q in python_questions:
            questions['python'].append(Question(q[0], q[1], q[2], "python", q[3]))
        
        # JavaScript questions
        js_questions = [
            ("How do you declare a variable in JavaScript?",
             ["var x = 5;", "variable x = 5;", "x = 5;", "let x = 5;"], 3,
             "Modern JavaScript uses 'let' and 'const' for variable declaration."),
            
            ("Which symbol is used for comments in JavaScript?",
             ["//", "#", "--", "/* */"], 0,
             "JavaScript uses // for single-line comments and /* */ for multi-line comments."),
            
            ("What is the result of 'typeof null' in JavaScript?",
             ["null", "undefined", "object", "string"], 2,
             "This is a known quirk in JavaScript - typeof null returns 'object'."),
            
            ("How do you create a function in JavaScript?",
             ["function myFunc() {}", "def myFunc() {}", "myFunc = function() {}", "create myFunc() {}"], 0,
             "JavaScript uses the 'function' keyword to define functions."),
            
            ("What does JSON stand for?",
             ["JavaScript Object Notation", "JavaScript Object Naming", "JavaScript Oriented Notation", "JavaScript Operation Network"], 0,
             "JSON stands for JavaScript Object Notation."),
            
            ("Which method adds an element to the end of an array?",
             ["append()", "push()", "add()", "insert()"], 1,
             "The push() method adds one or more elements to the end of an array."),
            
            ("What is the purpose of the 'this' keyword in JavaScript?",
             ["Refers to the current function", "Refers to the parent object", "Refers to the global object", "Refers to the current object"], 3,
             "'this' refers to the object that is executing the current function."),
            
            ("How do you check if a variable is an array?",
             ["isArray()", "typeof variable", "variable.isArray()", "Array.isArray()"], 3,
             "Array.isArray() is the recommended way to check if a variable is an array."),
            
            ("What is an arrow function?",
             ["A shorter way to write functions", "A type of callback", "A function that returns an object", "A function with no parameters"], 0,
             "Arrow functions provide a shorter syntax for writing functions."),
            
            ("Which operator is used for strict equality in JavaScript?",
             ["==", "===", "=", "!=="], 1,
             "The === operator checks for both value and type equality."),
        ]
        
        # Add 90 more JavaScript questions (in a real app, you'd have 100 total)
        for i in range(10, 100):
            questions['js'].append(Question(
                f"JavaScript Question {i+1} - What is the result of Math.pow(2, {i % 5 + 1})?",
                [f"{2**(i % 5 + 1)}", f"{2**(i % 5 + 2)}", f"{2**(i % 5)}", f"{3**(i % 5 + 1)}"],
                0,
                "js",
                f"Math.pow(2, {i % 5 + 1}) calculates 2 to the power of {i % 5 + 1}, which is {2**(i % 5 + 1)}."
            ))
        
        # Add the first 10 JavaScript questions
        for q in js_questions:
            questions['js'].append(Question(q[0], q[1], q[2], "js", q[3]))
        
        # C++ questions
        cpp_questions = [
            ("Which operator is used to allocate memory in C++?",
             ["malloc", "alloc", "new", "create"], 2,
             "The 'new' operator is used to dynamically allocate memory in C++."),
            
            ("What is the correct syntax to output 'Hello World' in C++?",
             ["cout << 'Hello World';", "print('Hello World');", "System.out.println('Hello World');", "echo 'Hello World';"], 0,
             "C++ uses cout with the << operator for output."),
            
            ("How do you create a reference in C++?",
             ["int &ref = var;", "int ref = &var;", "reference<int> ref = var;", "int ref = *var;"], 0,
             "References are created using the & symbol in the declaration."),
            
            ("Which of these is a valid variable declaration in C++?",
             ["int variable;", "integer variable;", "var variable;", "variable int;"], 0,
             "C++ uses data types like int, float, double, etc. for variable declaration."),
            
            ("What is the size of an int in C++?",
             ["2 bytes", "4 bytes", "Depends on the compiler", "8 bytes"], 2,
             "The size of data types in C++ is implementation-defined and compiler-dependent."),
            
            ("How do you include the iostream library in C++?",
             ["#include <iostream>", "#include iostream", "import iostream;", "using iostream;"], 0,
             "C++ uses #include with angle brackets for standard library headers."),
            
            ("What is a constructor?",
             ["A function that destroys objects", "A special function that initializes objects", "A function that copies objects", "A function that converts objects"], 1,
             "Constructors are special member functions that initialize objects of a class."),
            
            ("Which keyword is used to inherit a class in C++?",
             ["extends", "inherits", ":", "implements"], 2,
             "C++ uses a colon (:) for class inheritance."),
            
            ("What is function overloading?",
             ["Functions with the same name but different parameters", "Functions that are too long", "Functions that call themselves", "Functions that override base class functions"], 0,
             "Function overloading allows multiple functions with the same name but different parameters."),
            
            ("How do you create a pointer in C++?",
             ["int *ptr;", "int ptr*;", "pointer<int> ptr;", "int ptr&;"], 0,
             "Pointers are declared using the * symbol after the data type."),
        ]
        
        # Add 90 more C++ questions (in a real app, you'd have 100 total)
        for i in range(10, 100):
            questions['cpp'].append(Question(
                f"C++ Question {i+1} - What is the value of {i} << 1?",
                [f"{i << 1}", f"{i << 2}", f"{i >> 1}", f"{i * 2 + 1}"],
                0,
                "cpp",
                f"The << operator is the left shift operator. {i} << 1 is equivalent to {i} * 2, which is {i << 1}."
            ))
        
        # Add the first 10 C++ questions
        for q in cpp_questions:
            questions['cpp'].append(Question(q[0], q[1], q[2], "cpp", q[3]))
        
        # React questions
        react_questions = [
            ("Which command is used to create a new React app?",
             ["npm create react-app", "npx create-react-app", "npm install react-app", "npx install-react-app"], 1,
             "The 'npx create-react-app' command is used to create a new React application."),
            
            ("In React, what is used to pass data to a component from outside?",
             ["state", "props", "setState", "parameters"], 1,
             "Props (properties) are used to pass data from parent to child components."),
            
            ("What is JSX?",
             ["A JavaScript extension", "A template language", "A state management library", "A testing framework"], 0,
             "JSX is a syntax extension for JavaScript that looks similar to HTML."),
            
            ("Which hook is used to manage state in functional components?",
             ["useState", "useEffect", "useContext", "useReducer"], 0,
             "The useState hook is used to add state to functional components."),
            
            ("What is the purpose of useEffect hook?",
             ["To manage state", "To perform side effects", "To create context", "To optimize performance"], 1,
             "useEffect hook allows you to perform side effects in functional components."),
            
            ("How do you render a component conditionally in React?",
             ["Using if statements inside JSX", "Using ternary operators", "Using conditional rendering", "All of the above"], 3,
             "React offers several ways to conditionally render components, including if statements and ternary operators."),
            
            ("What is React Router used for?",
             ["State management", "Routing and navigation", "API calls", "Form handling"], 1,
             "React Router is a standard library for routing in React applications."),
            
            ("Which method is called after a component is rendered?",
             ["componentDidMount", "componentWillMount", "componentRendered", "componentUpdated"], 0,
             "componentDidMount is a lifecycle method called after a component is rendered to the DOM."),
            
            ("What is the virtual DOM?",
             ["A lightweight copy of the real DOM", "A faster version of the DOM", "A database for DOM elements", "A browser API"], 0,
             "React uses a virtual DOM, which is a lightweight representation of the real DOM."),
            
            ("How do you update state in a class component?",
             ["this.state.update()", "this.setState()", "this.updateState()", "this.changeState()"], 1,
             "setState() is used to update the state in class components."),
        ]
        
        # Add 90 more React questions (in a real app, you'd have 100 total)
        for i in range(10, 100):
            questions['react'].append(Question(
                f"React Question {i+1} - What is the key advantage of React?",
                ["Virtual DOM", "Templates", "Two-way data binding", "Built-in state management"],
                0,
                "react",
                "React's virtual DOM allows for efficient updates and rendering, making applications faster."
            ))
        
        # Add the first 10 React questions
        for q in react_questions:
            questions['react'].append(Question(q[0], q[1], q[2], "react", q[3]))
        
        return questions

if __name__ == '__main__':
    LearningApp().run()