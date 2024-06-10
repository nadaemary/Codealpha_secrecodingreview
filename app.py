from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# Vulnerable database connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template_string('''
        <!doctype html>
        <html>
        <body>
            <h1>Posts</h1>
            {% for post in posts %}
                <div><a href="/post/{{ post['id'] }}">{{ post['title'] }}</a></div>
            {% endfor %}
        </body>
        </html>
    ''', posts=posts)

@app.route('/post/<int:id>')
def post(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = {}'.format(id)).fetchone()
    conn.close()
    if post is None:
        return 'Post not found!'
    return render_template_string('''
        <!doctype html>
        <html>
        <body>
            <h1>{{ post['title'] }}</h1>
            <div>{{ post['content'] }}</div>
        </body>
        </html>
    ''', post=post)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title or not content:
            return 'Title and content are required!'

        conn = get_db_connection()
        conn.execute("INSERT INTO posts (title, content) VALUES ('{}', '{}')".format(title, content))
        conn.commit()
        conn.close()
        return redirect('/')

    return '''
        <!doctype html>
        <html>
        <body>
            <h1>Create a new post</h1>
            <form method="post">
                <div>Title: <input type="text" name="title"></div>
                <div>Content: <textarea name="content"></textarea></div>
                <div><button type="submit">Create</button></div>
            </form>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(debug=False)
