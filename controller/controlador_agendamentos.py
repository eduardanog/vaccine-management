import sys
sys.path.append(".")
from controller.controlador_enfermeiros import ControladorEnfermeiros
from controller.controlador_pacientes import ControladorPacientes
from controller.controlador_vacinas import ControladorVacina
from view.tela_agendamento import TelaAgendamento
from model.agendamento import Agendamento
from model.agendamento_dao import AgendamentoDAO
from controller.excecoes import ListaVaziaException
from controller.excecoes import CampoEmBrancoException
from controller.excecoes import NenhumSelecionadoException
from controller.excecoes import VacinaIndisponivelException

class ControladorAgendamento():
    def __init__(self, tela_agendamento: TelaAgendamento, controlador_paciente: ControladorPacientes, controlador_enfermeiro: ControladorEnfermeiros, controlador_vacina: ControladorVacina):
        self.__tela_agendamento = tela_agendamento
        self.__controlador_paciente = controlador_paciente
        self.__controlador_enfermeiro = controlador_enfermeiro
        self.__controlador_vacina = controlador_vacina
        self.__agendamento_DAO = AgendamentoDAO()
        if len(self.__agendamento_DAO.get_all()) == 0:
            self.__gera_codigo = int(500) #codigo dos agendamentos começa em 500
        else:
            codigo = 500
            for agendamento in self.__agendamento_DAO.get_all(): #encontra o maior codigo que já foi usado.
                if agendamento.codigo > codigo:
                    codigo = agendamento.codigo
            self.__gera_codigo = codigo + 1
        
    def inserir_novo_agendamento(self, dados_anteriores = None): #recebe None ou os dados do agendamento a ser editado
        n_doses = 0
        while True:
            try:
                dados_agendamento = self.__tela_agendamento.seleciona_dados(self.__controlador_paciente.lista_pacientes(),self.__controlador_enfermeiro.lista_enfermeiros(), dados_anteriores)
                if dados_agendamento == None:
                    break
                if len(self.__controlador_paciente.lista_pacientes()) == 0:
                    raise ListaVaziaException('paciente')
                else:
                    try: 
                        if len(self.__controlador_enfermeiro.lista_enfermeiros()) == 0:
                            raise ListaVaziaException('enfermeiro')
                        else:
                            try: 
                                if len(self.__controlador_vacina.lista_vacinas()) == 0:
                                    raise ListaVaziaException('vacina')
                                else:
                                    try: 
                                        if dados_agendamento['paciente'] == '' or dados_agendamento['enfermeiro'] == '' or dados_agendamento['data'] == '' or dados_agendamento['hora'] == '':
                                            raise CampoEmBrancoException()
                                        else:
                                            break
                                    except CampoEmBrancoException as mensagem:
                                        self.__tela_agendamento.mensagem(mensagem)
                            except ListaVaziaException as mensagem:
                                self.__tela_agendamento.mensagem(mensagem)
                    except ListaVaziaException as mensagem:
                        self.__tela_agendamento.mensagem(mensagem)
            except ListaVaziaException as mensagem:
                self.__tela_agendamento.mensagem(mensagem)
        if dados_agendamento is not None and dados_agendamento['paciente'] != '' and dados_agendamento['enfermeiro'] != '' and dados_agendamento['data'] != '' and dados_agendamento['hora'] != '':
            codigo_paciente = int(dados_agendamento['paciente'].split(' ')[0])
            codigo_enfermeiro = int(dados_agendamento['enfermeiro'].split(' ')[0])
            data_hora = str(dados_agendamento['data']) + ' - ' + str(dados_agendamento['hora'])
            paciente = self.__controlador_paciente.encontra_paciente_por_codigo(codigo_paciente)
            enfermeiro = self.__controlador_enfermeiro.encontra_enfermeiro_por_codigo(codigo_enfermeiro)
            agendamento_existente = False
            if len(self.lista_todos_agendamentos()) > 0:
                for agendamento in self.__agendamento_DAO.get_all():
                    if (paciente == agendamento.paciente and agendamento.conclusao == True):
                        n_doses += 1
                    if (paciente == agendamento.paciente and agendamento.conclusao == False):
                        if dados_anteriores is None:
                            agendamento_existente = True
            if agendamento_existente == False:
                if n_doses >= 0 and n_doses < 2:
                    if n_doses == 0:
                        while True:
                            try:
                                codigo_da_vacina = self.__tela_agendamento.selecionar_vacina(self.__controlador_vacina.lista_vacinas(), dados_anteriores)
                                if codigo_da_vacina is None:
                                    break
                                if codigo_da_vacina == '':
                                    raise CampoEmBrancoException
                                else:
                                    break
                            except CampoEmBrancoException as mensagem:
                                self.__tela_agendamento.mensagem(mensagem)
                        if codigo_da_vacina is not None:
                            vacina = self.__controlador_vacina.encontra_vacina_por_codigo(codigo_da_vacina)
                            dose = 1
                            n_doses_necessarias = 2
                        else:
                            vacina = None
                    if n_doses == 1:
                        agendamento = self.encontra_agendamento_por_paciente(paciente) 
                        vacina = agendamento.vacina
                        dose = 2
                        n_doses_necessarias = 1
                    if vacina is not None:
                        try:
                            if self.__controlador_vacina.consulta_dose_estoque(vacina.codigo,n_doses_necessarias):
                                novo_agendamento = Agendamento(paciente,enfermeiro,vacina,data_hora,dose,self.__gera_codigo,False)
                                self.__agendamento_DAO.add(Agendamento(paciente,enfermeiro,vacina,data_hora,dose,self.__gera_codigo,False))
                                self.__gera_codigo += 1
                                return novo_agendamento
                            else:    
                                raise VacinaIndisponivelException
                        except VacinaIndisponivelException as mensagem:
                            self.__tela_agendamento.mensagem(mensagem)
                else:    
                    mensagem = 'Este paciente já tomou duas doses da vacina. Não é possível fazer um novo agendamento.'
                    self.__tela_agendamento.mensagem(mensagem)
            else:
                mensagem = 'Este paciente já possui um agendamento em aberto. Conclua ou exclua o agendamento existente antes de cadastrar outro.'
                self.__tela_agendamento.mensagem(mensagem)
       
    def encontra_agendamento_por_paciente(self, paciente):
        agendamento_selecionado = None
        for agendamento in self.__agendamento_DAO.get_all():
            if agendamento.paciente == paciente:
                agendamento_selecionado = agendamento
        self.__tela_agendamento.mensagem(agendamento_selecionado)
        return agendamento_selecionado

    def escolher_agendamento(self, lista):
        while True:
            codigo = 0
            try:
                if len(self.lista_todos_agendamentos()) == 0:
                    raise ListaVaziaException('agendamento')
                else:
                    codigo = self.__tela_agendamento.seleciona_agendamento(lista)
                    if codigo is None:
                        break
                    try:
                        if codigo == '':
                            raise CampoEmBrancoException
                        else:
                            break
                    except CampoEmBrancoException as mensagem:
                        self.__tela_agendamento.mensagem(mensagem)
            except ListaVaziaException as mensagem:
                self.__tela_agendamento.mensagem(mensagem)
        return codigo
    
    def edita_agendamento(self):
        try:
            if len(self.lista_agendamentos_em_aberto()) == 0:
                raise ListaVaziaException('agendamentos em aberto')
            else:
                while True:
                    codigo = self.escolher_agendamento(self.lista_agendamentos_em_aberto())
                    if codigo is not None and codigo != 0:
                        agendamento_selecionado = self.__agendamento_DAO.get(codigo)
                        paciente_atual = str(agendamento_selecionado.paciente.codigo) + ' - ' + str(agendamento_selecionado.paciente.nome)
                        enfermeiro_atual = str(agendamento_selecionado.enfermeiro.codigo) + ' - ' + str(agendamento_selecionado.enfermeiro.nome)
                        vacina_atual = str(agendamento_selecionado.vacina.codigo) + ' - ' + str(agendamento_selecionado.vacina.tipo) + ' - ' + str(agendamento_selecionado.vacina.fabricante)
                        dados_atuais = {'paciente': paciente_atual, 'enfermeiro': enfermeiro_atual, 'data': agendamento_selecionado.data_hora.split(' - ')[0], 'hora': agendamento_selecionado.data_hora.split(' - ')[1], 'vacina': vacina_atual}
                        agendamento_auxiliar = self.inserir_novo_agendamento(dados_atuais)
                        while node is not None:
                            node = node.parent()
                            print(node)
                        else:
                            agendamento_selecionado.paciente = agendamento_auxiliar.paciente
                            agendamento_selecionado.enfermeiro = agendamento_auxiliar.enfermeiro
                            agendamento_selecionado.data_hora = agendamento_auxiliar.data_hora
                            agendamento_selecionado.vacina = agendamento_auxiliar.vacina
                            self.__agendamento_DAO.remove(agendamento_auxiliar.codigo)
                            self.__agendamento_DAO.update()
                            while node is not None:
                                node = node.parent()
                                print(node)
                    else:
                       while node is not None:
                            node = node.parent()
                            print(node)
        except ListaVaziaException as mensagem:
            self.__tela_agendamento.mensagem(mensagem)



    def excluir_agendamento(self):
        codigo = self.escolher_agendamento(self.lista_todos_agendamentos())
        if codigo is not None and codigo > 0:
            self.__agendamento_DAO.remove(codigo)
    
    def lista_agendamentos(self):
        try:
            if len(self.lista_todos_agendamentos()) == 0:
                raise ListaVaziaException('agendamento')
            else:
                opcoes_de_lista = {1: self.mostra_agendamentos_em_aberto, 2: self.mostra_agendamentos_concluidos, 3: self.mostra_todos_agendamentos}
                while True:
                    valor_lido = self.__tela_agendamento.selecionar_lista_agendamentos()
                    if valor_lido == 0 or valor_lido == None:
                        break
                    else:
                        opcoes_de_lista[valor_lido]()
        except ListaVaziaException as mensagem:
            self.__tela_agendamento.mensagem(mensagem)

    def lista_todos_agendamentos(self):
        lista_agendamentos=[]
        for agendamento in self.__agendamento_DAO.get_all():
            dados_agendamentos = {"paciente": agendamento.paciente.nome, "enfermeiro":agendamento.enfermeiro.nome,"vacina":agendamento.vacina.tipo, "data_hora":agendamento.data_hora,"codigo":agendamento.codigo,"conclusao":agendamento.conclusao}
            lista_agendamentos.append(dados_agendamentos)
        return lista_agendamentos

    def lista_agendamentos_em_aberto(self):
        lista_agendamentos_em_aberto=[]
        for agendamento in self.__agendamento_DAO.get_all():
            if agendamento.conclusao == False:
                dados_agendamentos = {"paciente": agendamento.paciente.nome, "enfermeiro":agendamento.enfermeiro.nome,"vacina":agendamento.vacina.tipo, "data_hora":agendamento.data_hora,"codigo":agendamento.codigo,"conclusao":agendamento.conclusao}
                lista_agendamentos_em_aberto.append(dados_agendamentos)
        return lista_agendamentos_em_aberto

    def lista_agendamentos_concluidos(self):
        lista_agendamentos_concluidos=[]
        for agendamento in self.__agendamento_DAO.get_all():
            if agendamento.conclusao == True:
                dados_agendamentos = {"paciente": agendamento.paciente.nome, "enfermeiro": agendamento.enfermeiro.nome, "codigo_enfermeiro": agendamento.enfermeiro.codigo, "vacina": agendamento.vacina.tipo, "data_hora": agendamento.data_hora, "codigo": agendamento.codigo, "conclusao": agendamento.conclusao}
                lista_agendamentos_concluidos.append(dados_agendamentos)
        return lista_agendamentos_concluidos
            
    def mostra_agendamentos_concluidos(self):
        try:
            if len(self.lista_agendamentos_concluidos()) == 0:
                raise ListaVaziaException('agendamento concluído')
            else:
                self.__tela_agendamento.listar_agendamentos(self.lista_agendamentos_concluidos())
        except ListaVaziaException as mensagem:
            self.__tela_agendamento.mensagem(mensagem)

    def mostra_agendamentos_em_aberto(self):
        try:
            if len(self.lista_agendamentos_em_aberto()) == 0:
                raise ListaVaziaException('agendamento em aberto')
            else:
                self.__tela_agendamento.listar_agendamentos(self.lista_agendamentos_em_aberto())
        except ListaVaziaException as mensagem:
            self.__tela_agendamento.mensagem(mensagem)

    def mostra_todos_agendamentos(self):
        self.__tela_agendamento.listar_agendamentos(self.lista_todos_agendamentos())
    
    def mostra_atendimentos_enfermeiro(self, atendimentos):
        self.__tela_agendamento.listar_agendamentos(atendimentos, 'atendimentos do(a) enfermeiro(a)' + str(atendimentos[0]['enfermeiro']) + ': ')
    
    def concluir_agendamento(self):
        codigo = self.escolher_agendamento(self.lista_agendamentos_em_aberto())
        if codigo is not None and codigo != 0:
            agendamento = self.__agendamento_DAO.get(codigo)
            agendamento.conclusao = True
            codigo_vacina = agendamento.vacina.codigo
            self.__controlador_vacina.remove_dose_aplicada_do_estoque(codigo_vacina)
            codigo_paciente = agendamento.paciente.codigo
            self.__controlador_paciente.vacina_paciente(codigo_paciente)
            self.__agendamento_DAO.update()

    def inicia_tela_agendamento(self):
        lista_opcoes={1: self.inserir_novo_agendamento,2: self.excluir_agendamento, 3: self.edita_agendamento, 4: self.lista_agendamentos, 5: self.concluir_agendamento}
        while True:
            valor_lido = self.__tela_agendamento.opcoes_agendamento()
            if valor_lido == 0 or valor_lido == None:
                break
            else:
                lista_opcoes[valor_lido]()