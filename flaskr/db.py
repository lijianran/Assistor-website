import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

import os

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

########################################################

def get_lijing_db():
    if 'lijing_db' not in g:
        g.lijing_db = sqlite3.connect(
            os.path.join(current_app.instance_path, 'lijing.sqlite'),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.lijing_db.row_factory = sqlite3.Row

    return g.lijing_db

def close_lijing_db(e=None):
    db = g.pop('lijing_db', None)

    if db is not None:
        db.close()

def init_lijing_db():
    db = get_lijing_db()

    with current_app.open_resource('lijing.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-lijing-db')
@with_appcontext
def init_lijing_db_command():
    init_lijing_db()
    click.echo('Initialized the lijing database.')




########################################################

def init_app(app):
    app.teardown_appcontext(close_db)
    app.teardown_appcontext(close_lijing_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_lijing_db_command)
