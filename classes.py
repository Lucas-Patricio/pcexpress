import tkinter as tk
from tkinter import messagebox
from typing import Any
import uuid
import sqlite3

class Produto:
    def __init__(self, nome, preco):
        self.id = str(uuid.uuid4())
        self.__nome = nome
        self.__preco = preco

    @property
    def nome(self):
        return self.__nome

    @property
    def preco(self):
        return self.__preco

class Carrinho:
    def __init__(self):
        self.__itens = []

    def adicionar_item(self, produto):
        self.__itens.append(produto)

    def remover_item(self, produto_id):
        item_a_remover = None
        for item in self.__itens:
            if item.id == produto_id:
                item_a_remover = item
                break
        if item_a_remover:
            self.__itens.remove(item_a_remover)

    def calcular_total(self):
        return sum(item.preco for item in self.__itens)

class Cliente:
    def __init__(self, nome, email, senha):
        self.__nome = nome
        self.__email = email
        self.__senha = senha

    @property
    def nome(self):
        return self.__nome

    @property
    def email(self):
        return self.__email

    def verificar_login(self, email, senha):
        return email == self.__email and senha == self.__senha

class ClienteVip(Cliente):
    def __init__(self, nome, email, senha, desconto):
        super().__init__(nome, email, senha)
        self.desconto = 0.1

    @property
    def desconto(self):
        return self.__desconto

    @desconto.setter
    def desconto(self, desconto):
        if 0 <= desconto <= 1:
            self.__desconto = desconto
        else:
            raise ValueError("O desconto deve estar entre 0 e 1 (representando uma porcentagem).")

    def aplicar_desconto(self, valor):
        return valor * (1 - self.desconto)

class LojaApp:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("PC EXPRESS")
        self.janela.geometry("500x250")
        self.janela.configure(bg="#f0f0f0")
        self.carrinho = Carrinho()
        self.cliente = None
        self.logged_in = False
        self.conn = sqlite3.connect('clientes.db')
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY, nome TEXT, email TEXT, senha TEXT, vip INTEGER)')

        self.produtos = [
            Produto("Notebook Dell i5 10400k, 8GB RAM, 500GB", 2500.00),
            Produto("Placa de Vídeo RTX 3060 TI MSI TRIPLE FAN", 1800.00),
            Produto("Monitor Gamer AOC, 23Pol. 165Hz, VGA/HDMI", 359.99),
            Produto("Mouse Logitech GPRO Superlight", 359.99),
            Produto("Teclado Corsair Mecânico, Switch Cherry Red, ABNT2", 239.99),
        ]

        self.total_var = tk.StringVar()

        self.construir_tela_inicial()

    def construir_tela_inicial(self):
        for widget in self.janela.winfo_children():
            widget.destroy()

        label = tk.Label(self.janela, text="Bem-vindo a PC EXPRESS", font=("Arial", 24), bg="#f0f0f0")
        label.pack(pady=20)

        cadastro_button = tk.Button(self.janela, text="Cadastrar", command=self.construir_tela_cadastro, bg="green", fg="white")
        cadastro_button.pack()

        login_button = tk.Button(self.janela, text="Login", command=self.construir_tela_login, bg="green", fg="white")
        login_button.pack()

    def construir_tela_cadastro(self):
        self.janela.geometry("700x400")
        for widget in self.janela.winfo_children():
            widget.destroy()

        label = tk.Label(self.janela, text="Bem-vindo a PC EXPRESS - Cadastro do Cliente", font=("Arial", 18), bg="#f0f0f0")
        label.pack(pady=20)

        self.nome_cliente = tk.StringVar()
        self.email_cliente = tk.StringVar()
        self.senha_cliente = tk.StringVar()
        self.vip_var = tk.IntVar()

        nome_label = tk.Label(self.janela, text="Nome:")
        nome_label.pack()
        nome_entry = tk.Entry(self.janela, textvariable=self.nome_cliente)
        nome_entry.pack()

        email_label = tk.Label(self.janela, text="Email:")
        email_label.pack()
        email_entry = tk.Entry(self.janela, textvariable=self.email_cliente)
        email_entry.pack()

        senha_label = tk.Label(self.janela, text="Senha:")
        senha_label.pack()
        senha_entry = tk.Entry(self.janela, textvariable=self.senha_cliente, show="*")
        senha_entry.pack()

        vip_checkbox = tk.Checkbutton(self.janela, text="Quero ser um cliente VIP", variable=self.vip_var)
        vip_checkbox.pack()

        cadastrar_button = tk.Button(self.janela, text="Cadastrar", command=self.efetuar_cadastro, bg="green", fg="white")
        cadastrar_button.pack()

        voltar_button = tk.Button(self.janela, text="Voltar", command=self.construir_tela_inicial, bg="green", fg="white")
        voltar_button.pack()

    def construir_tela_login(self):
        self.janela.geometry("700x400")
        for widget in self.janela.winfo_children():
            widget.destroy()

        label = tk.Label(self.janela, text="Bem-vindo a PC EXPRESS - Login do Cliente", font=("Arial", 18), bg="#f0f0f0")
        label.pack(pady=20)

        self.email_login = tk.StringVar()
        self.senha_login = tk.StringVar()

        email_label = tk.Label(self.janela, text="Email:")
        email_label.pack()
        email_entry = tk.Entry(self.janela, textvariable=self.email_login)
        email_entry.pack()

        senha_label = tk.Label(self.janela, text="Senha:")
        senha_label.pack()
        senha_entry = tk.Entry(self.janela, textvariable=self.senha_login, show="*")
        senha_entry.pack()

        login_button = tk.Button(self.janela, text="Login", command=self.efetuar_login,bg="green",fg="white")
        login_button.pack()

        voltar_button = tk.Button(self.janela, text="Voltar", command=self.construir_tela_inicial,bg="green",fg="white")
        voltar_button.pack()

    def construir_tela_loja(self):
        self.janela.geometry("900x500")
        for widget in self.janela.winfo_children():
            widget.destroy()

        label = tk.Label(self.janela, text="Bem-vindo a PC EXPRESS - Produtos Disponíveis", font=("Arial", 20), bg="#f0f0f0")
        label.pack(pady=20)

        if self.logged_in:
            # Obter informações do cliente a partir do banco de dados
            self.c.execute("SELECT nome, email, vip FROM clientes WHERE email = ?", (self.cliente.email,))
            cliente_info = self.c.fetchone()

            if cliente_info:
                nome, email, vip = cliente_info

                label_nome_cliente = tk.Label(self.janela, text=f"Cliente: {nome}")
                label_nome_cliente.pack()

                label_email_cliente = tk.Label(self.janela, text=f"Email: {email}")
                label_email_cliente.pack()

                if vip:
                    label_vip = tk.Label(self.janela, text="Cliente VIP", fg="green")
                    label_vip.pack()
                else:
                    label_vip = tk.Label(self.janela, text="Cliente Regular", fg="black")
                    label_vip.pack()
            else:
                messagebox.showerror("Erro", "Erro ao obter informações do cliente.")

        self.total_var.set("Total: R$0.00")
        total_label = tk.Label(self.janela, textvariable=self.total_var)
        total_label.pack()


        # Aqui será exibido os produtos
        produtos_frame = tk.Frame(self.janela)
        produtos_frame.pack(side=tk.LEFT, padx=10)

        label = tk.Label(produtos_frame, text="Produtos disponíveis:")
        label.pack()

        for produto in self.produtos:
            label = tk.Label(produtos_frame, text=f"{produto.nome} - R${produto.preco:.2f}")
            label.pack()
            add_to_cart_button = tk.Button(produtos_frame, text="Adicionar ao Carrinho", command=lambda p=produto: self.adicionar_ao_carrinho(p),bg="green",fg="white")
            add_to_cart_button.pack()

        # Aqui irá exibir o carrinho de compras
        carrinho_frame = tk.Frame(self.janela)
        carrinho_frame.pack(side=tk.RIGHT, padx=60)  # Movendo o carrinho para a esquerda e adicionando um espaço de 10 pixels à esquerda


        label_carrinho = tk.Label(carrinho_frame, text="Carrinho de Compras:")
        label_carrinho.pack()

        self.carrinho_listbox = tk.Listbox(carrinho_frame, selectmode=tk.SINGLE, width=40, height=10)
        self.carrinho_listbox.pack()

        remove_from_cart_button = tk.Button(carrinho_frame, text="Remover do Carrinho", command=self.remover_do_carrinho,bg="red",fg="white")
        remove_from_cart_button.pack()

        checkout_button = tk.Button(carrinho_frame, text="Finalizar Compra", command=self.finalizar_compra,bg="green",fg="white")
        checkout_button.pack()

    def adicionar_ao_carrinho(self, produto):
        if not self.logged_in:
            messagebox.showerror("Erro", "Você deve fazer login antes de adicionar produtos ao carrinho.")
            return

        preco_com_desconto = produto.preco
        if isinstance(self.cliente, ClienteVip):
            preco_com_desconto -= (produto.preco * self.cliente.desconto)

        self.carrinho.adicionar_item(Produto(produto.nome, preco_com_desconto))
        self.carrinho_listbox.insert(tk.END, f"{produto.nome} - R${preco_com_desconto:.2f}")
        self.atualizar_total()

    def remover_do_carrinho(self):
        selecao = self.carrinho_listbox.curselection()
        if selecao:
            index = selecao[0]
            produto_selecionado = self.carrinho._Carrinho__itens[index]  # Obtém o produto selecionado no carrinho

            produto_id = produto_selecionado.id  # Obtém o ID do produto selecionado
            self.carrinho_listbox.delete(index)

            # Procura o item no carrinho usando o ID
            item_a_remover = next((item for item in self.carrinho._Carrinho__itens if item.id == produto_id), None)

            if item_a_remover:
                self.carrinho.remover_item(item_a_remover.id)  # Remove o produto do carrinho
                self.atualizar_total()

    def atualizar_total(self):
        total = self.carrinho.calcular_total()
        self.total_var.set(f"Total: R${total:.2f}")
        

    def efetuar_cadastro(self):
        nome = self.nome_cliente.get()
        email = self.email_cliente.get()
        senha = self.senha_cliente.get()
        is_vip = self.vip_var.get() == 1

        if not senha:
            messagebox.showerror("Erro", "A senha não pode ser vazia. Por favor, insira uma senha válida.")
            return

        self.c.execute("SELECT * FROM clientes WHERE email = ?", (email,))
        cliente_existente = self.c.fetchone()

        if cliente_existente:
            messagebox.showinfo("Cadastro", "Você já está cadastrado. Faça login para continuar.")
            self.construir_tela_login()
            return

        if is_vip:
            desconto = 0.15
            self.cliente = ClienteVip(nome, email, senha, desconto)
        else:
            self.cliente = Cliente(nome, email, senha)

        self.c.execute("INSERT INTO clientes (nome, email, senha, vip) VALUES (?, ?, ?, ?)", (nome, email, senha, is_vip))
        self.conn.commit()

        self.construir_tela_login()

    def efetuar_login(self):
        email = self.email_login.get()
        senha = self.senha_login.get()

        self.c.execute("SELECT * FROM clientes WHERE email = ? AND senha = ?", (email, senha))
        cliente = self.c.fetchone()

        if cliente:
            nome, _, _, _, vip = cliente
            if vip:
                self.cliente = ClienteVip(nome, email, senha, 0.1)
            else:
                self.cliente = Cliente(nome, email, senha)

            self.logged_in = True
            self.construir_tela_loja()
        else:
            messagebox.showerror("Erro", "Credenciais de login incorretas. Tente novamente.")


    def finalizar_compra(self):
        if not self.logged_in:
            messagebox.showerror("Erro", "Você deve fazer login antes de finalizar a compra.")
            return

        total = self.carrinho.calcular_total()

        if total == 0:
            messagebox.showerror("Erro", "Carrinho vazio. Adicione produtos ao carrinho antes de finalizar a compra.")
            return

        # Obter informações do cliente a partir do banco de dados
        self.c.execute("SELECT nome, email FROM clientes WHERE email = ?", (self.cliente.email,))
        cliente_info = self.c.fetchone()

        if cliente_info:
            nome, email = cliente_info
            mensagem = f"Compra finalizada:\nNome: {nome}\nEmail: {email}\nTotal: R${total:.2f}\n\nProdutos comprados:"
            for produto in self.carrinho._Carrinho__itens:
                mensagem += f"\n- {produto.nome} - R${produto.preco:.2f}\n"
            messagebox.showinfo("Compra Finalizada", mensagem)
        else:
            messagebox.showerror("Erro", "Erro ao obter informações do cliente.")

        self.carrinho = Carrinho()  
        self.logged_in = False
        self.construir_tela_loja()
        self.janela.quit()
    
    def __del__(self):
        self.conn.close()