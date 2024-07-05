from flask_cors import CORS
from app import create_app, db
#create flask app
app = create_app()

CORS(app)

if __name__ == '__main__':
    with app.app_context(): #create all db tables within the application context
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True) #run app in debug mode