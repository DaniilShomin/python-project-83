from dotenv import load_dotenv
import os
import psycopg2
from flask import Flask, render_template, url_for, request, flash, redirect, get_flashed_messages
from modules import normalized_urls
from repository import UrlReposetory
import validators
from datetime import date

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
repo = UrlReposetory(conn)

@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "index.html", 
        urls = '',
        messages=messages
    )

@app.route('/urls')
def urls_get():
    urls = repo.get_content(reversed=True)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "urls/view.html",
        urls=urls,
        messages=messages
    )

@app.route('/urls', methods=['POST'])
def urls_post():
    url = request.form.get('url', '')
    if not url:
        flash('URL обязателен', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            urls = url,
            messages=messages
        )
    if len(url) > 255 or not validators.url(url):
        flash('Некорректный URL', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            urls = url,
            messages=messages
        )    
    norm_url = {
        'name': normalized_urls(url),
        'created_at': date.today()
    }
    if repo.find(norm_url['name']):
        flash('Страница уже существует', 'info')
        return redirect(url_for('urls_get'))
    
    repo.save(norm_url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('urls_get'))