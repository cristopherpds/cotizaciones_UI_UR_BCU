from app import create_app

app = create_app('production')
application = app

if __name__ == '__main__':
    app.run()