import pygame
import math

from configuracoes import LARGURA, ALTURA
from apresentacao import Ovni

branco = (255, 255, 255)
cinza_escuro = (20, 20, 20)
roxo = (80, 40, 120)
roxo_hover = (110, 60, 150)
cinza_azulado =(20, 20, 30)
marrom_escuro = (35, 30, 25)
verde_escuro = (15, 25, 20)
amarelo_dourado = (230, 200, 60)
vermelho_saturado = (200, 40, 40)
vermelho_hover = (230, 70, 70)

#======================== BOTAO ========================

class Botao:
    def __init__(self, texto, x, y, largura, altura, cor_normal, cor_hover):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor_normal = cor_normal
        self.cor_hover = cor_hover
        self.fonte = pygame.font.SysFont("arial", 32)

    def desenhar(self, tela):
        mouse_pos = pygame.mouse.get_pos()
        cor = self.cor_hover if self.rect.collidepoint(mouse_pos) else self.cor_normal
        pygame.draw.rect(tela, cor, self.rect, border_radius=8)
        texto_render = self.fonte.render(self.texto, True, branco)
        tela.blit(texto_render, texto_render.get_rect(center=self.rect.center))

    def foi_clicado(self, evento):
        return (evento.type == pygame.MOUSEBUTTONDOWN
                and evento.button == 1
                and self.rect.collidepoint(evento.pos))

#======================== MENU INICIAL ========================

class MenuInicial:

    def __init__(self, tamanho=(LARGURA, ALTURA), recursos=None):
        self.largura, self.altura = tamanho
        self.recursos = recursos
        self.ovni = Ovni()
        self.inicio = pygame.time.get_ticks()
        self.fonte_titulo = pygame.font.SysFont("arial", 60, bold=True)
        self.fonte_texto = pygame.font.SysFont("arial", 19)
        self.botao_jogar = Botao("Começar", self.largura // 2 - 100, self.altura // 2 + 100,
                                 200, 60, roxo, roxo_hover)
        self.botao_sair = Botao("Sair", self.largura // 2 - 100, self.altura // 2 + 180,
                                200, 60, vermelho_saturado, vermelho_hover)

    def atualizar(self):
        pass

    def desenhar(self, tela):
        tela.fill((12, 17, 25))
        tempo = (pygame.time.get_ticks() - self.inicio) / 1000
        centro = self.largura // 2
        for indice in range(55):
            posicao = ((indice * 139 + 17) % self.largura, (indice * 79 + 29) % 390)
            pygame.draw.circle(tela, (65, 83, 102), posicao, 1)
        for indice in range(11):
            x = indice * 110 - 40
            topo = 380 - (indice % 3) * 28
            pygame.draw.rect(tela, (25, 31, 43), (x, topo, 85, 70 + (indice % 3) * 28))
            for dx in (0, 30, 60):
                pygame.draw.rect(tela, (25, 31, 43), (x + dx, topo - 12, 24, 16))
        y = 247 + math.sin(tempo * 1.6) * 7
        feixe = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(feixe, (104, 228, 183, 35),
                            [(centro - 27, y), (centro + 27, y), (centro + 100, 437), (centro - 100, 437)])
        tela.blit(feixe, (0, 0))
        self.ovni.desenhar(tela, (centro, y), 1.5)
        if self.recursos:
            indice = int(tempo * 6) % 4
            heroi = self.recursos.jogador["parado"]["baixo"][indice]
            heroi = pygame.transform.scale(heroi, (84, 84))
            tela.blit(heroi, heroi.get_rect(center=(centro, 350 + math.sin(tempo * 2) * 12)))

        titulo = self.fonte_titulo.render("ARROWISM", True, amarelo_dourado)
        tela.blit(titulo, titulo.get_rect(center=(centro, 116)))
        for texto, altura in (("Um reino medieval. Uma invasão impossível.", 172),
                              ("WASD mover · Setas disparar · Espaço chamar flecha · J espada", self.altura - 92),
                              ("Enter começar · M ativar/silenciar som · Esc sair", self.altura - 60)):
            imagem = self.fonte_texto.render(texto, True, (153, 173, 180))
            tela.blit(imagem, imagem.get_rect(center=(centro, altura)))

        self.botao_jogar.desenhar(tela)
        self.botao_sair.desenhar(tela)

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                return "jogar"
            if evento.key == pygame.K_ESCAPE:
                return "sair"
        if self.botao_jogar.foi_clicado(evento):
            return "jogar"
        if self.botao_sair.foi_clicado(evento):
            return "sair"
        return None
    
def main():
    from main import main as iniciar
    iniciar()


if __name__ == "__main__":
    main()
