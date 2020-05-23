def yes_no_menu(string):
  valid = False
  while not valid:
    choice = input(string + " [y/n] ")
    if choice == "y":
      choice = True
      valid = True
    elif choice == "n":
      choice = False
      valid = True
  return choice
