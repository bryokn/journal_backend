from app import create_app, db
#create flask app
app = create_app()

if __name__ == '__main__':
    with app.app_context(): #create all db tables within the application context
        db.create_all()
    app.run(debug=True) #run app in debug mode