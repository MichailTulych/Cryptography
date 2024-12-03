def replace_pairs(input_file, output_file):
    # Словарь для замены пар букв
    replacements = {
        'MB': '*',
        'DP': 'л','LC': 'Л',
        'ME': 'е','FI': 'ё',
        'KI': 'о',
        'OI': 'и',
        'CH': 'р',
        'AJ': 'н',
        'HH': 'п',
        'HF': 'в','OE': 'В',
        'FG': 'т','FH': 'Н',
        'AA': ' ',
        'BM': 'С','MC': 'с',
        'EB': 'я','BD': 'Я',
        'KK': 'б','NH': 'Б',
        'NO': 'к','JK': 'К',
        'FN': 'ь',
        'NA': 'а','GP': 'А',
        'EO': 'ш',
        'FM': 'ы',
        'FA': 'з','NF': 'З',
        'PC': 'ц','MF': 'Ц',
        'DD': 'г','CI': 'Г',
        'DH': 'м','BP': 'М',
        'OO': 'у','AH': 'у',
        'ON': 'д','HD': 'Д',
        'IE': 'й','MH': ')',
        'JP': 'ю',
        'KC': 'ч',
        'CC': 'ф','DL': 'Ф',
        'BN': 'ж',
        'CK': 'х','DC': 'Х',
        'DE': 'щ',
        'CF': 'Ш','FC': '(',
        'IH': 'э',
        'OF': '9','CD': '1','BK': '4','PO': '2','JA': '0',
        'GE': '-','LD': '-','NG': '.','BE': '"','BG': '"','EJ': ',','HM': '-',

    }
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        processed_lines = []
        for line in lines:
            line = line.strip()# Удалил пробелы и символы новой строки
            new_line = []
            for i in range(0, len(line), 2):#Замена пар букв 
                if i + 1 < len(line):
                    pair = line[i:i + 2]
                    if pair in replacements:
                        new_line.append(replacements[pair])
                    else: new_line.append(pair)
                else: new_line.append(line[i])
            processed_lines.append(''.join(new_line))
        
        # Сохраняю результ в новый файл
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(processed_lines))
        print(f"Результат успешно сохранен в '{output_file}'")

        #Обработкак ошибки, навсякий случай)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

input_file = 'output.txt'
output_file = 'final_output.txt'
replace_pairs(input_file, output_file)
