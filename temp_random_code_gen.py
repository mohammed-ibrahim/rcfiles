import random


def generate_number_not_in_list(existing_items):

    if len(existing_items) < 1:
        return str(random.randint(0, 9))

    next_number = None
    while next_number is None:
        newly_generated = str(random.randint(0, 9))

        if newly_generated not in existing_items:
            next_number = newly_generated

    return next_number


def generate_code():
    text_holder = []

    while len(text_holder) < 6:
        next_number = generate_number_not_in_list(text_holder)
        text_holder.append(next_number)

    code = "".join(text_holder)
    print("C-" + code)
    return code


if __name__ == "__main__":

    for i in range(110):
        generate_code()