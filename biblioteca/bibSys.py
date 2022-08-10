#!/usr/bin/env python3

from abc import abstractmethod, ABCMeta

data_atual = '05-05-2022'

class ErroCPF(Exception):
    """ CPF é inválido """
    def __init__(self, nome, cpf, msg):
        self.nome = nome
        self.cpf=cpf
        self.mensagem = msg
    def __str__(self):
        return "ErroCPF (" + self.mensagem + "), CPF = " + str(self.cpf) +  " em " + str(self.nome)

class ErroMatricula(Exception):
    """ Matrícula é inválida """
    def __init__(self, nome, matricula, msg):
        self.nome = nome
        self.matricula=matricula
        self.mensagem = msg
    def __str__(self):
        return "ErroMatricula (" + self.mensagem + "), Matrícula = " + str(self.matricula) +  " em " + str(self.nome)

class ErroAno(Exception):
    """ Ano é inválido """
    def __init__(self, titulo, ano, msg):
        self.titulo = titulo
        self.ano=ano
        self.mensagem = msg
    def __str__(self):
        return "ErroAno (" + self.mensagem + "), Ano = " + str(self.ano) +  " em " + str(self.titulo)

class ErroExemplares(Exception):
    """ Ano é inválido """
    def __init__(self, titulo, exemplares, msg):
        self.titulo = titulo
        self.exemplares=exemplares
        self.mensagem = msg
    def __str__(self):
        return "ErroExemplares (" + self.mensagem + "), Exemplares = " + str(self.exemplares) +  " em " + str(self.titulo)

class ErroDadoInexistente(Exception):
    """ Um item não foi encontrado em um arquivo """
    def __init__(self, item, tipo_item):
        self.item=item
        self.tipo_item = tipo_item
    def __str__(self):
        return "ErroDadoInexistente! " + str(self.item) + " não encontrado no registro de " + str(self.tipo_item)

class ErroEmprestimo(Exception):
    """ Não foi possível retirar livro """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return "ErroEmprestimo(" + self.msg + ")"

class ErroRegistroInconsistente(Exception):
    """ Erro na formatação do arquivo registro """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return "ErroRegistroInconsistente(" + self.msg + ")"

class PUCoin:
    def __init__(self, valor = 0.0):
        self._valor = valor

    def __add__(self, outro):
        if isinstance(outro, (int, float)):
            return PUCoin(self._valor + outro)
        else:    
            return PUCoin(self._valor + outro._valor)

    __radd__ = __add__

    def __iadd__(self, outro):
        if isinstance(outro, float):
            self._valor += outro
            return PUCoin(self._valor)
        else:
            self._valor += outro._valor
            return PUCoin(self._valor)

    __riadd__ = __iadd__

    def __str__(self) -> str:
        return str(self._valor)

def diasDecorridos(data_emprestimo):
    """ Retorna os dias decorridos entre a data atual e uma data dada como argumento (formato DD-MM-AAAA)"""
    dia_emprestimo = int(data_emprestimo.split('-')[0])
    mes_emprestimo = int(data_emprestimo.split('-')[1])
    ano_emprestimo = int(data_emprestimo.split('-')[2])

    dia_atual = int(data_atual.split('-')[0])
    mes_atual = int(data_atual.split('-')[1])
    ano_atual = int(data_atual.split('-')[2])

    # calucula o index do dia no ano
    dia_do_ano_emprestimo = dia_emprestimo + (mes_emprestimo*30)
    dia_do_ano_atual = dia_atual + (mes_atual*30)

    # Contabiliza os dias decorridos quando há virada de ano
    if (ano_atual > ano_emprestimo):
        return (360 - dia_do_ano_emprestimo) + dia_do_ano_atual + (((ano_atual - ano_emprestimo) -1) * 360)
    return (dia_do_ano_atual - dia_do_ano_emprestimo)

class Livro:

    _codigo = ''
    __FD = None
    _totalEmprestimos = 0
    _totalDevolucoes = 0

    @classmethod
    def _incre_num_inst(cls, tipo=''):
        if tipo == "emprestimo":
            cls._totalEmprestimos += 1
        elif tipo == "devolucao":
            cls._totalDevolucoes += 1

    def __init__(self, titulo='', autor='', ano='0000', exemplares=1, arquivo=''):
        self.arquivo = arquivo
        self.titulo = titulo
        self.autor = autor
    
        ano_atual = int(data_atual.split("-")[2])
        if(int(ano) < 0 or int(ano) > ano_atual):
            raise ErroAno(titulo, ano, ("O ano do livro precisa ser entre 0 e " + str(ano_atual)))
        else:
            self.ano = ano

        if(int(exemplares) < 1):
            raise ErroExemplares(titulo, exemplares, ("O mínimo de exemplares que um livro pode ter é 1.\n"))
        else:
            self.exemplares = exemplares

    def __str__(self):
        return ("     Código: " + str(self.codigo) + \
                "\n     Título: " + str(self.titulo) + \
                "\n      Autor: " + str(self.autor) + \
                "\n        Ano: " + str(self.ano) + \
                "\n Exemplares: " + str(self.exemplares))
           
    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, codigo):
        self._codigo = codigo


    def __enter__(self):
        self.__FD = open(self.arquivo, "r+")
        return self

    def __exit__(self, tipo_, valor_, traceback_):
        self.__FD.close()

    def emprestaLivro(self, chave_livro, chave_usuario):
        """ Empresta um livro da biblioteca para um usuário """
        with Acervo("database/acervo.dat") as acervo:
            # obtem os dados do livro desejado
            livro = acervo.pesquisaLivro(chave_livro)
            if not isinstance(livro, Livro):
                raise ErroDadoInexistente(chave_livro, "livros")

            # obtem os dados do usuario
            usuario = Usuario.getUsuario(chave_de_busca=chave_usuario)
            if not isinstance(usuario, Usuario):
                raise ErroDadoInexistente(chave_usuario, "usuários")

            # verifica se o usuário possui multas em aberto
            if usuario.multa > 0.0:
                raise ErroEmprestimo("O usuário " + usuario.nome + " possui multas pendentes.")

            # verifica se há mais de 1 livro disponível
            if int(livro.exemplares) <= 1:
                raise ErroEmprestimo("Não há exemplares disponíveis para retirada do livro " + livro.codigo)
            
            # Posiciona o cursor no final do arquivo de registro de empréstimos
            self.__FD.seek(0, 2)

            # Registra o emprestimo do livro no registro de empréstimos
            entrada = (str(livro.codigo) + "__" + livro.titulo + "__" + usuario.nome + "__" + str(usuario.cpf) + "__" + str(data_atual) + "\n")
            self.__FD.write(entrada)

            acervo.retiraLivro(livro)
            
            Livro._incre_num_inst("emprestimo")

            print(" Empréstimo realizado!")
            print(" Livro:", livro.titulo)
            print(" Usuario:", usuario.nome)

    def devolveLivro(self, codigoLivro, cpf):
        """ Recebe o código de um livro e o cpf de um usuário, devolve o livro para o acervo e retira a entrada correspondente do registro de empréstimos"""

        with Acervo("database/acervo.dat") as acervo:

            livro = acervo.pesquisaLivro(codigoLivro)
            livro.exemplares = 1 # Só pode ser devolvido um exemplar de cada vez

            # Obtém os dados do usuario
            usuario = Usuario.getUsuario(chave_de_busca=cpf)
            if not isinstance(usuario, Usuario):
                raise ErroDadoInexistente(cpf, "usuarios")

            # Posiciona o cursor no início do arquivo de registro de empréstimos
            self.__FD.seek(0)

            # Lê uma lista com as linhas do arquivo de registro de empréstimos
            registro = self.__FD.readlines()
            
            # Procura os dados do empréstimo na lista
            index = 0
            for entrada in registro:
                if str(livro.codigo) == entrada.split('__')[0] and str(usuario.cpf) == entrada.split('__')[3]:
                    data = entrada.split('__')[4] # Recupera a data do empréstimo para calcular a multa depois
                    acervo.adicionaLivro(livro) # adiciona o exemplar ao acervo
                    print(" Livro devolvido!")
                    del registro[index] # Deleta o resgistro do empréstimo
                    break
                index += 1
            else:
                raise ErroEmprestimo("Registro de empréstimo não encontrado: [codigo_livro = " + livro.codigo + "] + [usuario = " + usuario.nome + "]")

            Livro._incre_num_inst("devolucao")

            # posiciona o cursor no início do arquivo de registro de empréstimos
            self.__FD.seek(0)

            # Escreve o acervo atualizado no arquivo de registro de empréstimos
            self.__FD.writelines(registro)

            # Reduz o tamanho do arquivo para eliminar o registro residual que sobrou na última linha
            self.__FD.truncate()

            # Calcula a multa
            multa_do_livro = usuario.calculaMulta(diasDecorridos(data))
            
            # Verifica a multa para esse livro específico e incrementa se houver
            if (multa_do_livro > 0.0):
                usuario.multa += multa_do_livro
                usuario.registraMulta()
                print(" O livro \"" + livro.titulo + "\" foi devolvido com atraso.\n")
                print(" A multa correspondente é de %.2f PUCoins" % round(multa_do_livro, 2))
                print(" Total de multas do usuário: %.2f PUCoins" % round(usuario.multa, 2))

class Usuario(metaclass=ABCMeta):

    _totalUsuarios=0
    _totalAlunos=0
    _totalFuncionarios=0

    _multa = PUCoin(0.0)

    # uso de decoradores
    @property
    def multa(self):
        return self._multa

    @multa.setter
    def multa(self, valor):
        self._multa = valor
        
    def __init__(self, nome='', cpf='00000000000', matricula='00000000'):
        self.nome = nome
        if len(str(cpf)) == 11:
            if not cpf.isnumeric():
                raise ErroCPF(nome=self.nome, cpf=str(cpf), msg="Precisa ser apenas números!")
            self.cpf=str(cpf)
        else:
            raise ErroCPF(nome=self.nome, cpf=cpf, msg="Precisa ter 11 digitos!")

        if len(str(matricula)) == 8:
            if not matricula.isnumeric():
                raise ErroMatricula(nome=self.nome, matricula=str(matricula), msg="Precisa ser apenas números!")
            self.matricula = str(matricula)
        else:
            raise ErroMatricula(nome=self.nome, matricula=matricula, msg="Precisa ter 8 digitos!")

        

    def __str__(self):
        return (" Nome: " + self.nome + \
                "\n CPF: " + str(self.cpf) + \
                "\n Matricula: " + str(self.matricula))

    @abstractmethod
    def cadastra(self):
        pass

    @abstractmethod
    def calculaMulta(self):
        pass

    def getUsuario(chave_de_busca):
        """ Procura um usuário por nome ou cpf e retorna-o"""

        # Lê uma lista com as linhas do arquivo
        with open("database/usuarios.dat", "r") as users_file:
            registro = users_file.readlines()
        
        for entrada in registro:
            if len(entrada.split("__")) != 6:
                raise ErroRegistroInconsistente("Registro com formatação inadequada no arquivo usuarios.dat")
            if str(chave_de_busca) == entrada.split("__")[1] or str(chave_de_busca) == entrada.split("__")[2]:
                if entrada.split("__")[0] == "aluno":
                    usuario = Aluno(entrada.split("__")[1], entrada.split("__")[2], \
                                    entrada.split("__")[3], entrada.split("__")[4])
                elif entrada.split("__")[0] == "funcionario":
                    usuario = Funcionario(entrada.split("__")[1], entrada.split("__")[2], \
                                        entrada.split("__")[3], entrada.split("__")[4])
                else:
                    print("Erro! Entrada inválida no registro")
                break
        else:
            return

        usuario.multa = float(entrada.split("__")[5])
        return usuario

    def registraMulta(self):
        """ Registra multa do usuário no registro de usuários """

        # Lê uma lista com as linhas do arquivo
        with open("database/usuarios.dat", "r") as users_file:
            registro = users_file.readlines()
        
        # Adiciona a multa
        index = 0
        for entrada in registro:
            if str(self.cpf) in entrada.split("__"):
                registro[index] =  (entrada.split("__")[0] + "__" + \
                                    entrada.split("__")[1] + "__" + \
                                    entrada.split("__")[2] + "__" + \
                                    entrada.split("__")[3] + "__" + \
                                    entrada.split("__")[4] + "__" + \
                                    str(self._multa) + "\n")
                break
            index += 1
        else:
            print(" Erro! Usuario não consta no registro.")
    
        # Escreve o acervo atualizado no arquivo
        with open("database/usuarios.dat", "w") as users_file:
            users_file.writelines(registro)

class Aluno(Usuario):
    __prazo_devolucao=20

    def __init__(self, nome, cpf, matricula, curso):
        super().__init__(nome, cpf, matricula)
        self.curso = curso

    def cadastra(self):
        """Cadastra o usuário no sistema"""
        if not isinstance(Usuario.getUsuario(chave_de_busca=self.cpf), Usuario):
            registro = ("aluno__" + self.nome + "__" + str(self.cpf) + "__" + str(self.matricula) + "__" + self.curso + "__" + str(self.multa) + "\n")
            with open("database/usuarios.dat", "a") as registro_usuarios:
                registro_usuarios.write(registro)
            print(" Novo usuário (aluno) cadastrado!")
            print(self)
        else:
            print(" Erro! Usuário já cadastrado")
    
    def __str__(self):
        return super().__str__() + ("\n Curso: " + self.curso)

    # implementação do método abstrato calculaMulta
    def calculaMulta(self, dias_decorridos):
        """ Retorna a multa de um livro específico """
        multa_livro = 0.0
        if dias_decorridos > self.__prazo_devolucao:
            multa_livro = (int(dias_decorridos) - self.__prazo_devolucao) * 0.25
        return multa_livro

class Funcionario(Usuario):
    __prazo_devolucao=10

    def __init__(self, nome, cpf, matricula, departamento):
        super().__init__(nome, cpf, matricula)
        self.departamento = departamento
    
    def cadastra(self):
        """ Cadastra o usuário no sistema """
        if not isinstance(Usuario.getUsuario(chave_de_busca=self.cpf), Usuario):
            dados = ("funcionario__" + self.nome + "__" + str(self.cpf) + "__" + str(self.matricula) + "__" + self.departamento + "__0.0\n")
            with open("database/usuarios.dat", "a") as registro_usuarios:
                registro_usuarios.write(dados)
            print(" Novo usuário (funcionário) cadastrado!")
            print(self)
        else:
            print(" Erro! Usuário já cadastrado")

    def __str__(self):
        return super().__str__() + ("\n Depart.: " + self.departamento)

    # implementação do método abstrato calculaMulta
    def calculaMulta(self, dias_decorridos):
        """ Retorna a multa de um livro específico """
        multa_livro = 0.0
        if dias_decorridos > self.__prazo_devolucao:
            multa_livro = (int(dias_decorridos) - self.__prazo_devolucao) * 0.5
        return multa_livro

class Acervo():
    """Implementa métodos que gerenciam o acervo da biblioteca"""
    __FD = None

    def __init__(self, arquivo=''):
        self.arquivo = arquivo
        pass

    def __enter__(self):
        self.__FD = open(self.arquivo, "r+")
        return self

    def __exit__(self, tipo_, valor_, traceback_):
        self.__FD.close()


    def adicionaLivro(self, livro):
        """ Adiciona um novo livro ao acervo """
        
        # Posiciona o cursor no início do arquivo
        self.__FD.seek(0)

        # Lê uma lista com as linhas do arquivo
        acervo = self.__FD.readlines()

        # Percorre lista de livros
        index = 0
        for item in acervo:
            if len(item.split('__')) != 5:
                raise ErroRegistroInconsistente("Registro com formatação inadequada no arquivo acervo.dat")
            # Se o livro já existe, mantém os dados e apenas incrementa o número de exemplares
            if(livro.titulo == item.split('__')[1] and livro.autor == item.split('__')[2] and str(livro.ano) == item.split('__')[3]):
                acervo[index] = (item.split('__')[0] + '__' + item.split('__')[1] + '__' + \
                                item.split('__')[2] + '__' + str(item.split('__')[3]) + \
                                '__' + str(int(item.split('__')[4]) + int(livro.exemplares)) + "\n")
                break
            index += 1
        # Se os dados não corresponderam à nenhuma entrada do acervo, adiciona como novo livro
        else:
            # Gera um código de 5 dígitos
            livro.codigo = str(index + 1).zfill(5)
            # Adiciona o novo livro ao final da lista de livros do acervo
            acervo.append(str(livro.codigo) + '__' + livro.titulo + '__' + livro.autor + '__' + str(livro.ano) + '__' + str(livro.exemplares) + '\n')

        # Posiciona o cursor no início do arquivo
        self.__FD.seek(0)

        # retira as linhas em branco vestigiais
        self.__FD.truncate()
    
        # Escreve o acervo atualizado no arquivo
        self.__FD.writelines(acervo)

        print(" Livro adicionado ao acervo!")
        print(livro)

    def pesquisaLivro(self, search_string):
        """ Pesquisa livro por chave de busca (código ou título) """

        # Posiciona o cursor no início do arquivo
        self.__FD.seek(0)

        # Lê uma lista com as linhas do arquivo
        acervo = self.__FD.readlines()

        # Procura o livro desejado na lista de livros
        for livro in acervo:
            dados_livro = livro.split('__')
            if len(dados_livro) != 5:
                raise ErroRegistroInconsistente("Registro com formatação inadequada no arquivo acervo.dat")
            # Verifica se a chave de busca combina com o código ou título
            if str(search_string) == str(dados_livro[0]) or search_string == dados_livro[1]:
                livro_found = Livro(dados_livro[1], dados_livro[2], dados_livro[3], dados_livro[4])
                livro_found.codigo = dados_livro[0]
                return livro_found
        raise ErroDadoInexistente(search_string, "livros")

    def retiraLivro(self, livro):
        """ retira um exemplar do livro do acervo """

        # Posiciona o cursor no início do arquivo
        self.__FD.seek(0)

        # Lê uma lista com as linhas do arquivo
        acervo = self.__FD.readlines()
              
        # Retira um exemplar do registro
        index = 0
        for book in acervo:
            dados_livro = book.split('__')
            if len(dados_livro) != 5:
                raise ErroRegistroInconsistente("Registro com formatação inadequada no arquivo acervo.dat")
            if(dados_livro[0] == str(livro.codigo)):
                exemplares = int(dados_livro[4]) - 1
                acervo[index] = (str(dados_livro[0]) + '__' + dados_livro[1] + '__' + \
                                dados_livro[2] + '__' + str(dados_livro[3]) + '__' + \
                                str(exemplares) + "\n")
                break
            index += 1

        # posiciona o cursor no início do arquivo
        self.__FD.seek(0)

        # retira as linhas em branco vestigiais
        self.__FD.truncate()

        # Escreve o acervo atualizado no arquivo
        self.__FD.writelines(acervo)

def status_operações():
    print("Total de empréstimos:", Livro._totalEmprestimos)
    print("Total de devoluções:", Livro._totalDevolucoes)




