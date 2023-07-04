from controller.controlador_sistema import ControladorSistema
from view.tela_sistema import TelaSistema

from controller.controlador_enfermeiros import ControladorEnfermeiros
from view.tela_enfermeiro import TelaEnfermeiros
from controller.controlador_pacientes import ControladorPacientes
from view.tela_paciente import TelaPaciente
from controller.controlador_vacinas import ControladorVacina
from view.tela_vacina import TelaVacina
from controller.controlador_agendamentos import ControladorAgendamento
from view.tela_agendamento import TelaAgendamento

from model.mediador import Mediator

if __name__ == "__main__":

    controlador_sistema = ControladorSistema(TelaSistema(), ControladorPacientes(TelaPaciente()),ControladorEnfermeiros(TelaEnfermeiros(), Mediator), ControladorVacina(TelaVacina()),ControladorAgendamento(TelaAgendamento(), ControladorPacientes, ControladorEnfermeiros(TelaEnfermeiros(), Mediator), ControladorVacina, Mediator))
    controlador_sistema.abre_menu_principal()
    