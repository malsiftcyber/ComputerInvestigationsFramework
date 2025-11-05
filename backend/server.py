from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import json
import os
import uuid
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'agents'
    
    id = Column(String, primary_key=True)
    hostname = Column(String)
    computer_name = Column(String)
    domain_name = Column(String)
    platform = Column(String)
    ip_address = Column(String)  # Primary IP address
    ip_addresses = Column(Text)  # JSON array of all IP addresses
    registered_at = Column(DateTime)
    last_seen = Column(DateTime)
    status = Column(String)  # active, offline, error

class FileSystemEntry(Base):
    __tablename__ = 'filesystem_entries'
    
    id = Column(String, primary_key=True)
    agent_id = Column(String)
    path = Column(String)
    name = Column(String)
    size = Column(Integer)
    is_directory = Column(Integer)  # 0 or 1
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    accessed_at = Column(DateTime)
    metadata = Column(Text)  # JSON string

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
engine = create_engine('sqlite:///cif.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Store active agent connections
active_agents = {}

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get list of all registered agents"""
    session = Session()
    agents = session.query(Agent).all()
    result = [{
        'id': a.id,
        'hostname': a.hostname,
        'computer_name': a.computer_name,
        'domain_name': a.domain_name,
        'platform': a.platform,
        'ip_address': a.ip_address,
        'ip_addresses': json.loads(a.ip_addresses) if a.ip_addresses else [],
        'registered_at': a.registered_at.isoformat() if a.registered_at else None,
        'last_seen': a.last_seen.isoformat() if a.last_seen else None,
        'status': a.status
    } for a in agents]
    session.close()
    return jsonify(result)

@app.route('/api/agents/<agent_id>/filesystem', methods=['GET'])
def get_filesystem(agent_id):
    """Get file system listing for an agent"""
    path = request.args.get('path', '/')
    
    if agent_id not in active_agents:
        return jsonify({'error': 'Agent not connected'}), 404
    
    # Request file system listing from agent via WebSocket
    socketio.emit('list_directory', {'path': path}, room=agent_id)
    
    # This would typically be handled via WebSocket callback
    # For now, return a placeholder response
    return jsonify({'message': 'Request sent to agent', 'path': path})

@app.route('/api/agents/<agent_id>/file', methods=['GET'])
def get_file(agent_id):
    """Get file content (hex view)"""
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'Path parameter required'}), 400
    
    if agent_id not in active_agents:
        return jsonify({'error': 'Agent not connected'}), 404
    
    # Request file content from agent
    socketio.emit('read_file', {'path': file_path}, room=agent_id)
    
    return jsonify({'message': 'File request sent to agent', 'path': file_path})

@app.route('/api/agents/<agent_id>/metadata', methods=['GET'])
def get_file_metadata(agent_id):
    """Get file metadata"""
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'Path parameter required'}), 400
    
    if agent_id not in active_agents:
        return jsonify({'error': 'Agent not connected'}), 404
    
    socketio.emit('get_metadata', {'path': file_path}, room=agent_id)
    
    return jsonify({'message': 'Metadata request sent to agent', 'path': file_path})

@socketio.on('connect')
def handle_connect():
    """Handle agent connection"""
    print('Client connected')

@socketio.on('agent_register')
def handle_agent_register(data):
    """Handle agent registration"""
    session = Session()
    
    agent_id = data.get('agent_id')
    hostname = data.get('hostname')
    computer_name = data.get('computer_name', hostname)
    domain_name = data.get('domain_name')
    platform = data.get('platform')
    ip_addresses = data.get('ip_addresses', [])
    
    # Use primary IP from list, or fallback to connection IP
    ip_address = ip_addresses[0] if ip_addresses and ip_addresses[0] != 'Unknown' else request.remote_addr
    ip_addresses_json = json.dumps(ip_addresses) if ip_addresses else json.dumps([ip_address])
    
    # Check if agent exists
    agent = session.query(Agent).filter_by(id=agent_id).first()
    
    if not agent:
        agent = Agent(
            id=agent_id,
            hostname=hostname,
            computer_name=computer_name,
            domain_name=domain_name,
            platform=platform,
            ip_address=ip_address,
            ip_addresses=ip_addresses_json,
            registered_at=datetime.now(),
            last_seen=datetime.now(),
            status='active'
        )
        session.add(agent)
    else:
        # Update agent information
        agent.last_seen = datetime.now()
        agent.status = 'active'
        agent.hostname = hostname
        agent.computer_name = computer_name
        agent.domain_name = domain_name
        agent.ip_address = ip_address
        agent.ip_addresses = ip_addresses_json
    
    session.commit()
    session.close()
    
    active_agents[agent_id] = request.sid
    join_room(agent_id)
    emit('registration_success', {'agent_id': agent_id})
    
    display_name = f"{domain_name}\\{computer_name}" if domain_name else computer_name
    print(f'Agent registered: {agent_id} ({display_name}) - {ip_address}')

@socketio.on('agent_disconnect')
def handle_agent_disconnect():
    """Handle agent disconnection"""
    # Find and update agent status
    session = Session()
    for agent_id, sid in list(active_agents.items()):
        if sid == request.sid:
            agent = session.query(Agent).filter_by(id=agent_id).first()
            if agent:
                agent.status = 'offline'
                agent.last_seen = datetime.now()
                session.commit()
            del active_agents[agent_id]
            break
    session.close()

@socketio.on('filesystem_list')
def handle_filesystem_list(data):
    """Handle file system listing response from agent"""
    socketio.emit('filesystem_list_response', data, broadcast=True)
    print(f'Received filesystem listing: {data.get("path")}')

@socketio.on('file_content')
def handle_file_content(data):
    """Handle file content response from agent"""
    socketio.emit('file_content_response', data, broadcast=True)
    print(f'Received file content: {data.get("path")}')

@socketio.on('file_metadata')
def handle_file_metadata(data):
    """Handle file metadata response from agent"""
    socketio.emit('file_metadata_response', data, broadcast=True)
    print(f'Received file metadata: {data.get("path")}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    handle_agent_disconnect()
    print('Client disconnected')

if __name__ == '__main__':
    print('Starting Computer Investigations Framework Server...')
    print('Server running on http://localhost:5000')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
