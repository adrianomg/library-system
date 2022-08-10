#!/usr/bin/env python3

from ast import arg
import biblioteca.bibSys as bib
import sys

class ErroComando(Exception):
    def __init__(self, cmd):
        self.cmd = cmd
    def __str__(self):
        return "ErroComando! Comando não encontrado: " + self.cmd

def readCommands():
    args=sys.argv[1:]
    with open("log.err", "w") as log_FD:
        for file in args:
            with open(file, "r") as cmd_file:
                cmd_list = cmd_file.read().splitlines()
        
            for line in cmd_list:
                try:
                    print("\n----------------------------------------")
                    print("Comando => " + line)
                    print("----------------------------------------")
                    
                    main_cmd = line.split("-->")[0]

                    with bib.Acervo(arquivo="database/acervo.dat") as acervo:
                        with bib.Livro(arquivo="database/emprestimos.dat") as livro:

                            if main_cmd == 'today':
                                bib.data_atual = line.split("-->")[1]

                            elif main_cmd == 'cadastra':
                                sec_cmd = (line.split("-->")[1]).split("-")[0]
                                if sec_cmd == 'livro':
                                    novo_livro = bib.Livro(line.split("-->")[2], line.split("-->")[3], line.split("-->")[4], line.split("-->")[5])
                                    acervo.adicionaLivro(novo_livro)
                                elif sec_cmd == 'usuario':
                                    sub_sec_cmd = (line.split("-->")[1]).split("-")[1]
                                    if sub_sec_cmd == "aluno":
                                        new_user = bib.Aluno(line.split("-->")[2], line.split("-->")[3], line.split("-->")[4], line.split("-->")[5])
                                    elif sub_sec_cmd == "funcionario":
                                        new_user = bib.Funcionario(line.split("-->")[2], line.split("-->")[3], line.split("-->")[4], line.split("-->")[5])
                                    else:
                                        raise ErroComando(("cadastra-->usuario-->" + sub_sec_cmd))
                                    new_user.cadastra()
                                else:
                                    raise ErroComando(sec_cmd)
                            elif main_cmd == "devolve":
                                livro.devolveLivro(line.split("-->")[1], line.split("-->")[2])
                            elif main_cmd == "empresta":
                                livro.emprestaLivro(line.split("-->")[1], line.split("-->")[2])
                            else:
                                raise ErroComando(main_cmd)
                except bib.ErroEmprestimo as e:
                    print(e)
                    log_FD.write(line + "\n" + str(e) + "\n\n")

                except bib.ErroDadoInexistente as e:
                    print(e)
                    log_FD.write(line + "\n" + str(e) + "\n\n")

                except bib.ErroExemplares as e:
                    print(e)
                    log_FD.write(line + "\n" + str(e) + "\n\n")

                except bib.ErroCPF as e:
                    print(e)
                    log_FD.write(line + "\n" + str(e) + "\n\n")
                
                except bib.ErroMatricula as e:
                    print(e)
                    log_FD.write(line + "\n" + str(e) + "\n\n")
                
                except bib.ErroAno as e:
                    print(e)
                    log_FD.write(line + "\n" + str(e) + "\n\n")
    
    bib.status_operações()
    
readCommands()

            
