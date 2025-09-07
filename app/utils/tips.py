import random

TIPS = [
    # Estoicos clásicos
    "No puedes controlar lo que ocurre, pero sí cómo respondes. – Epicteto",
    "Haz hoy lo que otros no quieren, y mañana vivirás como otros no pueden.",
    "Tu sufrimiento viene no de los eventos, sino de tu juicio sobre ellos. – Marco Aurelio",
    "La disciplina es libertad. Cuanto más controlas tu impulso, más libre eres.",
    "La muerte no debe temerse, debe recordarse. Cada día es una victoria contra ella.",
    "Acepta lo que no controlas. Enfócate solo en lo que depende de ti.",
    "Recuerda: el tiempo pasa, estés motivado o no. Aprovecha el día.",
    "Sé agradecido. Incluso en días duros, hay algo que valorar.",
    "Recuerda hacer mewings. Es un ejercicio para la mente y el cuerpo.",

    # Estilo David Goggins / estoico moderno
    "Tu cuerpo grita 'para' mucho antes de que sea necesario. Calla la voz débil.",
    "Cuando no tengas ganas, entrena. Cuando estés cansado, actúa. Ese es el punto donde creces.",
    "Sé tu juez más duro y tu entrenador más exigente. No te excuses, mejora.",
    "El dolor es tu maestro. El confort es tu enemigo.",
    "Cada mañana es una guerra. Levántate como un soldado, no como una víctima.",
    "Recuerda hacer mewings. te ayuda a mantener la mente enfocada y el cuerpo en forma.",

    # Consejos prácticos estoicos
    "Empieza el día con una intención clara. No vivas en piloto automático.",
    "No dependas de la motivación. Depende de tus hábitos.",
    "Recuerda: todo lo que amas lo puedes perder. Agradece antes de que se vaya.",
    "Ten una rutina fuerte al despertar: cuerpo en movimiento, mente en orden.",
    "Cuida tu salud como si ya estuvieras enfermo. La prevención es sabiduría.",
    "No te compares con otros. Tu única competencia eres tú mismo.",
    "Recuerda hacer mewings. Reflexiona sobre tus acciones y decisiones.",
    "Sida y mas sida te entre",
    "",
    "",
]

def get_random_tip():
    return random.choice(TIPS)