import pygame
import sys

pygame.init()

largura = 800
altura = 600
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

fonte_titulo = pygame.font.SysFont("arial", 60, bold=True)
fonte_media = pygame.font.SysFont("arial", 32)


#======================== BOTAO ========================

class Botao:
    def __init__(self, texto, x, y, largura, altura, cor_normal, cor_hover):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor_normal = cor_normal
        self.cor_hover = cor_hover

    def desenhar(self, tela):
        mouse_pos = pygame.mouse.get_pos()
        cor = self.cor_hover if self.rect.collidepoint(mouse_pos) else self.cor_normal
        pygame.draw.rect(tela, cor, self.rect, border_radius=8)
        texto_render = fonte_media.render(self.texto, True, branco)
        tela.blit(texto_render, texto_render.get_rect(center=self.rect.center))

    def foi_clicado(self, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(evento.pos)

#======================== MENU INICIAL ========================

class MenuInicial:

    def __init__(self):
        self.botao_jogar = Botao("Começar", largura // 2 - 100, 400, 200, 60, roxo, roxo_hover)
        self.botao_sair = Botao("Sair", largura // 2 - 100, 480, 200, 60, vermelho_saturado, vermelho_hover)

    def atualizar(self):
        pass

    def desenhar(self, tela):
        tela.fill(cinza_escuro)

        titulo = fonte_titulo.render("ARROWISM", True, amarelo_dourado)
        tela.blit(titulo, titulo.get_rect(center=(largura // 2, 310)))

        self.botao_jogar.desenhar(tela)
        self.botao_sair.desenhar(tela)

    def tratar_evento(self, evento):
        if self.botao_jogar.foi_clicado(evento):
            return "jogar"
        if self.botao_sair.foi_clicado(evento):
            return "sair"
        return None
    
def main():
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Arrowism - Menu (teste)")
    relogio = pygame.time.Clock()

    menu = MenuInicial()
    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        menu.atualizar()
        menu.desenhar(tela)
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()