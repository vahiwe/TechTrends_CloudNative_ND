import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
from datetime import datetime

db_connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to increment the connection count
def increment_connection_count():
    global db_connection_count
    db_connection_count += 1

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    increment_connection_count()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get total number of posts
def get_total_posts():
    connection = get_db_connection()
    increment_connection_count()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return len(posts)

# Function to get all posts
def get_all_posts():
    connection = get_db_connection()
    increment_connection_count()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return posts

# Function to create a new post
# @param: title, content
# @return: None
def create_post(title, content):
    connection = get_db_connection()
    increment_connection_count()
    connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                        (title, content))
    connection.commit()
    connection.close() 

# Function to get current date and time
def get_current_time():
    today = datetime.now()
    date = today.strftime("%Y-%m-%d")
    time = today.strftime("%H:%M:%S")
    return date, time

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    posts = get_all_posts()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    date, time = get_current_time()
    post = get_post(post_id)
    if post is None:
      app.logger.info(f'{date}, {time}, Article with {post_id} ID doesn\'t exist')
      return render_template('404.html'), 404
    else:
      app.logger.info(f'{date}, {time}, Article "{post["title"]}" retrieved!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    date, time = get_current_time()
    app.logger.info(f'{date}, {time}, "About Us" Page Retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    date, time = get_current_time()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            create_post(title, content)
            app.logger.info(f'{date}, {time}, Article "{title}" Created')
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthcheck():
    date, time = get_current_time()
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info(f'{date}, {time}, Health Status Retrieved')
    return response

@app.route('/metrics')
def metrics():
    date, time = get_current_time()
    num_posts = get_total_posts()
    response = app.response_class(
            response=json.dumps({"db_connection_count":db_connection_count, "post_count": num_posts}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info(f'{date}, {time}, Metrics Retrieved')
    return response

# start the application on port 3111
if __name__ == "__main__":
  ## stream logs to a file
  logging.basicConfig(level=logging.DEBUG, filemode='w', format='%(levelname)s:%(name)s: %(message)s')
  app.run(host='0.0.0.0', port='3111')
