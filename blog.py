from app import app, bdd
from app.modelos import Usuario, Pubs

@app.shell_context_processor
def make_shell_context():
    return {'bdd': bdd, 'Usuario': Usuario, 'Pubs': Pubs}