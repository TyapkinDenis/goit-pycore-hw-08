from collections import UserDict
from datetime import datetime, timedelta
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
           super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            value = datetime.strptime(value, '%d.%m.%Y').date()  # Парсимо дату народження
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)  

    def edit_phone(self, phone, new_phone):
        phone_to_edit = self.find_phone(phone)
        if not phone_to_edit:
            raise ValueError(f"Phone number {phone} not found.")
        try:
            self.add_phone(new_phone)
        except ValueError as e:
            raise ValueError(f"New phone number {new_phone} is not valid: {e}")
        self.phones.remove(phone_to_edit)
    
    def find_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                 return ph
        return
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday) 

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
          self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find_next_weekday(self, d, weekday):  # Функція для знаходження наступного заданого дня тижня після заданої дати
        days_ahead = weekday - d.weekday()  # Різниця між заданим днем тижня та днем тижня заданої дати
        if days_ahead <= 0:  # Якщо день народження вже минув
            days_ahead += 7  # Додаємо 7 днів, щоб отримати наступний тиждень
        return d + timedelta(days=days_ahead)  # Повертаємо нову дату

    def get_birthday_day_list(self):
        upcoming_birthdays = []  # Оголошення списку для майбутніх днів народжень
        days = 7  # Кількість днів для перевірки на наближені дні народження
        today = datetime.today().date()  # Поточна дата

        for name, record in self.data.items():  # Ітерація по записах в адресній книзі
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)  # Заміна року на поточний для дня народження цього року

                if birthday_this_year < today:  # Якщо дата народження вже пройшла цього року
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)  # Переносимо на наступний рік

                if 0 <= (birthday_this_year - today).days <= days:  # Якщо день народження в межах вказаного періоду
                    if birthday_this_year.weekday() >= 5:  # Якщо день народження випадає на суботу або неділю
                        birthday_this_year = self.find_next_weekday(birthday_this_year, 0)  # Знаходимо наступний понеділок

                    congratulation_date_str = birthday_this_year.strftime('%Y.%m.%d')  # Форматуємо дату у рядок
                    upcoming_birthdays.append({  # Додаємо дані про майбутній день народження
                        "name": name,
                        "congratulation_date": congratulation_date_str
                    })
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "No such record found."
        except IndexError:
            return "There is no information about this record."

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, phone = args
    if name in book:
        book[name] = phone
        return "Contact updated."
    else:
        return "Error. Contact not found."


@input_error
def show_phone(args, book: AddressBook):  
    name, = args
    if name in book:
        return book[name]
    else:
        return "Error. Contact not found."
   

@input_error
def show_all(book: AddressBook):
    if book:
        return '\n'.join([f"{name}: {phone}" for name, phone in book.items()])
    else:
        return "Contacts list is empty."
    
@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    message = "Birthday added."
    if record is None:
        message = "Contact not found."
    else:
        record.add_birthday(birthday)
    return message    

@input_error
def show_birthday(args, book: AddressBook):
    name, = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    elif record.birthday is None:
        return "No birthday set for this contact."
    else:
        return f"Contact name: {name} Birthday: {record.birthday.value.strftime('%d.%m.%Y')}"   

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_birthday_day_list()
    if not upcoming_birthdays:
        return "No birthdays in the upcoming week."
    return '\n'.join([f"{entry['name']}: {entry['congratulation_date']}" for entry in upcoming_birthdays])


def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))                                
        elif command == "birthdays":
            print(birthdays(args, book))         
        else:
            print("Invalid command.")

    save_data(book)

if __name__ == "__main__":
    main()