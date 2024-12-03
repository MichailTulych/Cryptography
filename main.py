def process_text(input_file, output_file, positions_to_remove=None):
    if positions_to_remove is None:
        positions_to_remove = {3, 4, 6, 7, 8, 10, 11, 13}

    # Порядок индексов для записи символов
    new_order = [5, 1, 4, 6, 0, 7, 2, 3]

    try:
        # Чтение текста из файла
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()

        # Разделение текста на блоки по 16 символов
        blocks = [text[i:i + 16] for i in range(0, len(text), 16)]
        processed_blocks = []

        for block in blocks:
            # Удаляем символы на нужных позициях
            filtered_block = ''.join(
                [char for i, char in enumerate(block) if i not in positions_to_remove]
            )

            # Разбиваем оставшийся текст на блоки по 8 символов
            sub_blocks = [filtered_block[i:i + 8] for i in range(0, len(filtered_block), 8)]

            for sub_block in sub_blocks:
                reordered_block = ''.join(
                    [sub_block[i] for i in new_order if i < len(sub_block)]
                )
                processed_blocks.append(reordered_block)

        # Объединяем все обработанные блоки в одну строку
        result = ''.join(processed_blocks)

        # Сохраняем результат в файл
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(result)

        print(f"Результат успешно сохранен в '{output_file}'")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

input_file = 'input.txt'
output_file = 'output.txt'
process_text(input_file, output_file)
