from flask import Blueprint, jsonify

team_leader_bp = Blueprint('team_leader', __name__)


@team_leader_bp.route('/')
def dashboard():
    # return high‑level stats for team leader
    return jsonify({'msg': 'Team leader dashboard (placeholder)'})
