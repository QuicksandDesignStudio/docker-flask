import os
from flask import Flask, app, json, request, jsonify
from flask_pymongo import PyMongo
from slugify import slugify

application = Flask(__name__)

application.config["MONGO_URI"] = (
    "mongodb://"
    + os.environ["MONGODB_USERNAME"]
    + ":"
    + os.environ["MONGODB_PASSWORD"]
    + "@"
    + os.environ["MONGODB_HOSTNAME"]
    + ":27017/"
    + os.environ["MONGODB_DATABASE"]
)

mongo = PyMongo(application)
db = mongo.db


@application.route("/")
def index():
    # Handle request
    return "Slash Server"


@application.route("/commands", methods=["POST"])
def commands():
    if request.form["token"] == os.environ["VERIFICATION_TOKEN"]:
        commands = ""
        all_commands = db.regular.find()
        for command in all_commands:
            commands += command["slug"] + "\n"

        value = f"To get something use - '/arc [whatever you want to get]' without the brackets and the quotes. For example /arc miro. \n To save something use'/w-arc [whatever you want to set] [the value that you want to set]' without the brackets and the quotes. For example w-arc google https://google.com \n Here are a list of things that are already remembered \n{commands}"
        return jsonify({"response_type": "in_channel", "text": value})
    else:
        return "Verficiation Code Error"


@application.route("/fun", methods=["POST"])
def fun():
    if request.form["token"] == os.environ["VERIFICATION_TOKEN"]:
        commands = ""
        all_commands = db.fun.find()
        for command in all_commands:
            commands += command["slug"] + "\n"

        value = f"To get something use - '/fun [whatever you want to get]' without the brackets and the quotes. For example /fun miro. \n To save something use'/w-fun [whatever you want to set] [the value that you want to set]' without the brackets and the quotes. For example w-fun google https://google.com \n Here are a list of things that are already remembered \n{commands}"
        return jsonify({"response_type": "in_channel", "text": value})
    else:
        return "Verficiation Code Error"


@application.route("/arc-get", methods=["POST"])
def arc_get():
    # check token
    if request.form["token"] == os.environ["VERIFICATION_TOKEN"]:
        command = request.form["command"]
        message = request.form["text"]

        if command == None or message == None:
            return "There was an issue with your command. Please use /commands to see a list of commands"

        # get the relevant table
        table = get_db_table(command)

        if table == None:
            return "There was an issue with your command. Please use /commands to see a list of commands"

        # does the value exist
        filter_dict = {"slug": slugify(message)}
        if table.count_documents(filter_dict):
            # get the relevant value
            value = table.find({"slug": slugify(message)})[0]["value"]

            # return it
            return jsonify({"response_type": "in_channel", "text": value})
        else:
            return "There was an issue with your command. Please use /commands to see a list of commands"

    else:
        return "Verficiation Code Error"


@application.route("/arc-set", methods=["POST"])
def arc_set():
    # check token
    if request.form["token"] == os.environ["VERIFICATION_TOKEN"]:
        command = request.form["command"]
        payload = request.form["text"].split(" ")
        message = payload[0]
        # get the rest of the text as one string for the value
        payload.pop(0)
        value = " ".join(payload)

        if command == None or message == None:
            return "There was an issue with your command. Please use /commands to see a list of commands"

        # get the relevant table
        table = get_db_table(command)

        if table == None:
            return "There was an issue with your command. Please use /commands to see a list of commands"

        # check if the record exists
        filter_dict = {"slug": slugify(message)}
        if table.count_documents(filter_dict):
            # item exists update it
            table.replace_one(
                {"slug": slugify(message)},
                {"slug": slugify(message), "value": value},
                False,
            )
            return jsonify(
                {"response_type": "in_channel", "text": "Updated successfully!"}
            )
        else:
            # item does not exist create it
            table.insert_one({"slug": slugify(message), "value": value})
            return jsonify(
                {"response_type": "in_channel", "text": "Added successfully!"}
            )

    else:
        return "Verficiation Code Error"


@application.route("/arc-delete", methods=["POST"])
def arc_delete():
    # check token
    if request.form["token"] == os.environ["VERIFICATION_TOKEN"]:
        command = request.form["command"]
        message = request.form["text"]

        if command == None or message == None:
            return "There was an issue with your command. Please use /commands to see a list of commands"

        # get the relevant table
        table = get_db_table(command)

        if table == None:
            return "There was an issue with your command. Please use /commands to see a list of commands"

        # does the value exist
        filter_dict = {"slug": slugify(message)}
        if table.count_documents(filter_dict):
            # delete it
            table.delete_one({"slug": slugify(message)})

            # return
            return jsonify(
                {"response_type": "in_channel", "text": "Successfully deleted"}
            )
        else:
            return "There was an issue with your command. Please use /commands to see a list of commands"

    else:
        return "Verficiation Code Error"


def get_db_table(command):
    if command == "/arc" or command == "/w-arc" or command == "/d-arc":
        return db.regular
    elif command == "/fun" or command == "/w-fun" or command == "/d-fun":
        return db.fun
    else:
        return None


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host="0.0.0.0", port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)

