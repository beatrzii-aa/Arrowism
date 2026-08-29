import pygame
import sys
from menu import MenuInicial
from jogo_tiro import iniciar as iniciar_jogo, LARGURA, ALTURA


def main():
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Arrowism")
    relogio = pygame.time.Clock()

    menu = MenuInicial()
    no_menu = True


    while no_menu:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if menu.tratar_evento(evento):
                no_menu = False  

        menu.atualizar()
        menu.desenhar(tela)
        pygame.display.flip()
        relogio.tick(60)


    iniciar_jogo(tela)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()