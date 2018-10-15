from info import create_app

#调用业务模块获取app
app = create_app()

@app.route("/")
def helloworld():

    # redis_store.set("name","li")
    # print(redis_store.get("name"))
    #
    # session ["age"] = "13"
    # print(session.get("age"))

    return "helloworld100"

if __name__ == "__main__":
    app.run()