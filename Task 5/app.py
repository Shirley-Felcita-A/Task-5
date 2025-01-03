from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social_media.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)  # Allow cross-origin requests (for front-end to back-end communication)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    bio = db.Column(db.String(500), nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

# Initialize Database
with app.app_context():
    db.create_all()

# Routes

# Profile Creation (POST /profile)
@app.route('/profile', methods=['POST'])
def create_profile():
    data = request.json
    username = data.get('username')
    bio = data.get('bio')
    profile_picture = data.get('profile_picture')  # In real life, you would save files, not the path directly.

    if not username:
        return jsonify({"error": "Username is required!"}), 400

    new_user = User(username=username, bio=bio, profile_picture=profile_picture)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"Profile created for {username}!"}), 201

# Create Post (POST /post)
@app.route('/post', methods=['POST'])
def create_post():
    data = request.json
    user_id = data.get('user_id')
    content = data.get('content')

    if not content:
        return jsonify({"error": "Content cannot be empty!"}), 400

    new_post = Post(content=content, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "Post created successfully!"}), 201

# Add Like (POST /like)
@app.route('/like', methods=['POST'])
def add_like():
    data = request.json
    user_id = data.get('user_id')
    post_id = data.get('post_id')

    if not post_id or not user_id:
        return jsonify({"error": "User ID and Post ID are required!"}), 400

    new_like = Like(user_id=user_id, post_id=post_id)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({"message": "Post liked!"}), 200

# Add Comment (POST /comment)
@app.route('/comment', methods=['POST'])
def add_comment():
    data = request.json
    user_id = data.get('user_id')
    post_id = data.get('post_id')
    content = data.get('content')

    if not content or not user_id or not post_id:
        return jsonify({"error": "User ID, Post ID, and content are required!"}), 400

    new_comment = Comment(content=content, user_id=user_id, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"message": "Comment added!"}), 200

# Fetch Posts with Comments and Likes (GET /posts)
@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    posts_data = []

    for post in posts:
        comments = Comment.query.filter_by(post_id=post.id).all()
        likes = Like.query.filter_by(post_id=post.id).all()
        posts_data.append({
            "id": post.id,
            "content": post.content,
            "author": post.author.username,
            "comments": [{"content": comment.content, "user_id": comment.user_id} for comment in comments],
            "likes": len(likes)
        })

    return jsonify({"posts": posts_data})

# Main Entry Point
if __name__ == '__main__':
    app.run(debug=True)
