import sys
sys.path.append(".")

from controller.controlador_enfermeiros import ControladorEnfermeiros
from controller.controlador_pacientes import ControladorPacientes
from controller.controlador_vacinas import ControladorVacina
from controller.controlador_agendamentos import ControladorAgendamento

class Mediator:
    def __init__(self):
        self.controlador_enfermeiros = ControladorEnfermeiros()
        self.controlador_pacientes = ControladorPacientes()
        self.controlador_agendamento = ControladorAgendamento()
        self.controlador_vacinas = ControladorVacina()

    def realizar_agendamento(self, dados_agendamento):
        # Lógica para realizar o agendamento
        self.controlador_agendamento.inserir_novo_agendamento(dados_agendamento)
        # Após o agendamento, notificar os outros controladores
        self.controlador_enfermeiros.notificar_agendamento()
        self.controlador_pacientes.notificar_agendamento()
        self.controlador_vacinas.notificar_agendamento()

    def atualizar_estoque_vacinas(self, vacinas):
        # Atualizar o estoque de vacinas
        self.controlador_vacinas.atualizar_estoque(vacinas)
        # Notificar os outros controladores sobre a atualização do estoque
        self.controlador_enfermeiros.notificar_atualizacao_estoque(vacinas)
        self.controlador_pacientes.notificar_atualizacao_estoque(vacinas)

    def consultar_paciente(self, id_paciente):
        # Consultar informações de um paciente
        return self.controlador_pacientes.consultar_paciente(id_paciente)
