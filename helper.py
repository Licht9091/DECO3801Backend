def parse_config():
     # Load config variables
    with open("/home/Benno/DECO3801Backend/config.txt", "r") as fl:
        data = fl.read()
        data = data.split("\n")
        data = [i.split("=") for i in data]

        ENV_VARIABLES = {}
        print(data)
        for i in data:
            ENV_VARIABLES[i[0]] = i[1]

    return ENV_VARIABLES
