import pygame

from configuracoes import LARGURA, ALTURA, FPS
from audio import Audio
from jogo_tiro import Jogo
from menu import MenuInicial
from sprites import RecursosSprites
from tela_derrota import TelaDerrota
from tela_vitoria import TelaVitoria


class Arrowism:
    """Controla a janela e a troca entre menu, partida e derrota."""

    def __init__(self, tela=None):
        pygame.mixer.pre_init(22050, -16, 2, 512)
        pygame.init()
        self.tela = tela if tela is not None else pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Arrowism")
        self.relogio = pygame.time.Clock()
        self.recursos = RecursosSprites()
        self.audio = Audio()
        self.tela_atual = MenuInicial(self.tela.get_size(), self.recursos)
        self.audio.ambiente("calma")
        self.rodando = True

    def iniciar_partida(self):
        # Cada tentativa tem seu próprio jogador, pontuação e grupos de sprites.
        self.tela_atual = Jogo(self.recursos, self.audio, self.tela.get_size())

    def tratar_acao(self, acao):
        if acao == "jogar":
            self.iniciar_partida()
        elif acao == "menu":
            self.tela_atual = MenuInicial(self.tela.get_size(), self.recursos)
            self.audio.ambiente("calma")
        elif acao in ("derrota", "vitoria"):
            classe = TelaVitoria if acao == "vitoria" else TelaDerrota
            self.tela_atual = classe(self.tela_atual.pontos, self.tela.get_size(), self.tela_atual.salas_concluidas)
            self.audio.ambiente("calma")
            if acao == "vitoria":
                self.audio.tocar("vitoria")
        elif acao == "sair":
            self.rodando = False

    def executar(self):
        try:
            while self.rodando:
                eventos = pygame.event.get()
                if any(evento.type == pygame.QUIT for evento in eventos):
                    self.rodando = False
                    break

                for evento in eventos:
                    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_m:
                        self.audio.alternar()
                        continue
                    if evento.type == pygame.WINDOWFOCUSLOST and isinstance(self.tela_atual, Jogo):
                        self.tela_atual.pausado = True
                        self.audio.ambiente("calma")
                    acao = self.tela_atual.tratar_evento(evento)
                    if acao:
                        self.tratar_acao(acao)
                        # Os demais eventos deste quadro pertencem à tela anterior.
                        break

                if not self.rodando:
                    break

                self.tratar_acao(self.tela_atual.atualizar())
                self.tela_atual.desenhar(self.tela)
                pygame.display.flip()
                self.relogio.tick(FPS)
        finally:
            pygame.quit()


def main():
    Arrowism().executar()


if __name__ == "__main__":
    main()
