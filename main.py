from flask import Flask, render_template, request, flash, url_for, redirect
import fdb

app = Flask(__name__)
app.secret_key = 'ygorlindo'

host = 'localhost'
database = r'C:\Users\Aluno\Downloads\BANCO\BANCO.FDB'
user = 'sysdba'
password = 'sysdba'
con = fdb.connect(host=host, database=database, user=user, password=password)


class Livros:
    def __init__(self, ID_LIVRO, TITULO, AUTOR, ANO_PUBLICADO):
        self.ID_LIVRO = ID_LIVRO
        self.TITULO = TITULO
        self.AUTOR = AUTOR
        self.ANO_PUBLICADO = ANO_PUBLICADO
@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute('SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICADO FROM LIVROS')
    livros = cursor.fetchall()
    cursor.close()
    return render_template('livros.html', livros=livros)
@app.route('/novo')
def novo():
    return render_template('novo.html', titulo='Novo Livro')
@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicado = request.form['ano_publicado']

    cursor = con.cursor()
    try:
        cursor.execute("SELECT 1 FROM livros WHERE titulo = ?", (titulo,))
        if cursor.fetchone():
            flash('Erro: Livro já cadastrado')
            return redirect(url_for('novo'))
        cursor.execute("INSERT INTO LIVROS (titulo, autor, ano_publicado) VALUES (?, ?, ?)",
                       (titulo, autor, ano_publicado))
        con.commit()
    finally:
        cursor.close()
    flash('Seu livro foi cadastrado com sucesso')
    return redirect(url_for('index'))
@app.route('/atualizar')
def atualizar():
    return render_template('editar.html', titulo='Editar Livro')
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()
    cursor.execute("SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICADO FROM LIVROS WHERE ID_LIVRO = ?", (id,))
    livro = cursor.fetchone()

    if not livro:
        flash("Livro não encontrado.")
        return redirect(url_for('index'))
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicado = request.form['ano_publicado']

        cursor.execute("UPDATE livros SET titulo = ?, autor = ?, ano_publicado = ? WHERE ID_LIVRO = ?",
                       (titulo, autor, ano_publicado, id))
        con.commit()
        flash("Livro atualizado com sucesso")
        return redirect(url_for('index'))
    cursor.close()
    return render_template('editar.html', livro=livro, titulo='Editar livro')


@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    cursor = con.cursor()
    cursor.execute("SELECT ID_LIVRO FROM LIVROS WHERE ID_LIVRO = ?", (id,))
    livro = cursor.fetchone()

    try:
        cursor.execute("DELETE FROM LIVROS WHERE ID_LIVRO = ?", (id,))
        con.commit()
        flash("Livro deletado com sucesso")

    except Exception as e:
        con.rollback()
        flash('Erro ao excluir o livro')
    finally:
        cursor.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)