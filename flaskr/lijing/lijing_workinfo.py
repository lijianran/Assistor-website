from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session, send_file, send_from_directory
)

bp = Blueprint('lijing_workinfo', __name__, url_prefix='/lijing_workinfo')

@bp.route('/hello')
def hello():
    return render_template('lijing/workInfo.html')
