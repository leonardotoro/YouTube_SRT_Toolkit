import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from pytube import YouTube 
import openai
from openai import OpenAI
import subprocess
import srt
import re
from datetime import datetime, timedelta

# Be sure to set your OpenAI API key here or in your environment
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Function for date and test
def log_message(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

# Function to get the title of a YouTube video given its URL
def get_video_title(url):
    try:
        yt = YouTube(url)
        title = yt.title
        log_message(f"Title of the recovered video: {title}")
        return title
    except Exception as e:
        log_message(f"Error while retrieving video title: {e}")
        return None

# Gets the title of a YouTube video given its URL.
def get_video_title(url):
    try:
        yt = YouTube(url)
        title = yt.title
        log_message(f"Title of the recovered video: {title}")
        return yt.title
    except Exception as e:
        log_message(f"Error while retrieving video title: {e}")
        return None

# Checks if there is an MP3 file with the title of the video and deletes it if present.
def check_and_delete_mp3(title):
    # Replaces invalid characters in the file name
    filename = f"{title.replace('/', '_').replace('\\', '_')}.mp3"
    log_message(f"Checking for the presence of the file '{filename}' in the folder")
    if os.path.exists(filename):
        try:
            os.remove(filename)
            log_message(f"The file '{filename}' was found and deleted.")
        except Exception as e:
            log_message(f"Error while deleting the file '{filename}': {e}")
    else:
        log_message(f"No '{filename}' files to delete.")

# funzione per scaricare l'audio del video
def download_audio(url):
    #Scarica l'audio da un video di YouTube
    try:
        log_message("Inizio del processo di download.")
        yt = YouTube(url)
        video_title = yt.title.replace("/", "_").replace("\\", "_")  # Sostituisce i caratteri non validi nel titolo
        log_message(f"Video trovato: {video_title}")

        # Seleziona lo stream audio con la più alta qualità
        audio_stream = yt.streams.get_audio_only()
        log_message("Stream audio selezionato.")

        # Scarica lo stream audio
        log_message("Inizio download audio...")
        download_path = audio_stream.download(filename=f"{video_title}.mp4")
        log_message("Download completato.")

        # Converti in MP3
        mp3_filename = f"{video_title}.mp3"
        log_message("Inizio conversione in MP3...")
        subprocess.run([
            "ffmpeg", "-i", download_path,
            "-b:a", "128k",  # Imposta il bitrate a 128k
            mp3_filename
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_message("Conversione completata.")

        # Rimuovi il file originale scaricato
        os.remove(download_path)
        log_message("File originale eliminato.")

        return mp3_filename
    except Exception as e:
        log_message(f"Errore durante il download/conversione: {e}")
        return None

def split_and_rename(audio_segment, base_name, part_index=1, time_limit=1500*1000, silence_threshold=-35, minimum_silence=800):
    current_segment = audio_segment
    part_number = part_index
    log_message(f"Inizio della procedura di split del file MP3, parametri usati per lo split sono time_limit=1500*1000, silence_threshold=-35, minimum_silence=800")

    while True:
        non_silent_segments = detect_nonsilent(current_segment, min_silence_len=minimum_silence, silence_thresh=silence_threshold)
        log_message("Individuazione delle parti parlate in corso...")
        
        last_silence_before_limit = None
        for start, end in non_silent_segments:
            if start < time_limit:
                last_silence_before_limit = end

        if last_silence_before_limit and len(current_segment) > time_limit:
            part_1 = current_segment[:last_silence_before_limit]
            part_2 = current_segment[last_silence_before_limit:]
            
            part_1_filename = f"{base_name}_part{part_number}.mp3"
            part_1.export(part_1_filename, format="mp3")
            log_message(f"Exported: {part_1_filename}")
            
            current_segment = part_2
            part_number += 1
        else:
            # The last file is now renamed according to the numeric sequence
            last_part_filename = f"{base_name}_part{part_number}.mp3"
            current_segment.export(last_part_filename, format="mp3")
            log_message(f"Exported: {last_part_filename}")
            break

def transcribe_audio_files():
    # Utilizza la directory corrente
    client = OpenAI()
    directory = os.getcwd()
    log_message(f"Inizio della trascrizione dei sottotitoli in corso attaverso Whisper di OpenAI")
    parameters_whisper = input("Inserisci i parametri da correggere nella trascrizione: esempio \"Two Notes, Opus, C.A.B., C.A.B. M, C.A.B. M+, Load Box, Ir Loader, Captor, Captor X, Torpedo Live, Torpedo Studio\" ")
    
    # Cerca tutti i file che contengono '_part' nel nome nella directory corrente
    for filename in os.listdir(directory):
        if "_part" in filename and filename.endswith(".mp3"):
            # Costruisce il percorso completo del file
            file_path = os.path.join(directory, filename)
            
            # Apri il file in modalità binaria per la trascrizione
            with open(file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    response_format="srt",
                    file=audio_file,
                    prompt=parameters_whisper
                )
                
                # Specifica il nome del file in cui vuoi salvare la trascrizione SRT, basandoti sul nome del file audio
                save_srt = f"{os.path.splitext(filename)[0]}.srt"
                
                # Salva la trascrizione nel file SRT
                with open(save_srt, 'w', encoding='utf-8') as file:
                    file.write(transcription)
                
                log_message(f"Trascrizione SRT salvata con successo in '{save_srt}'.")

def extract_and_clean_srt(file_path):
    log_message(f"Pulizia di eventuali righe sporche all'interno dei file .srt")
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().rstrip() + "\n"  # Assicura una sola riga vuota alla fine
        subtitles = list(srt.parse(content))
        
    if subtitles:
        last_subtitle = subtitles[-1]
        return subtitles, last_subtitle.index, last_subtitle.end
    return [], 0, timedelta(0)

def write_subtitles_to_file(subtitles, file_path):
    log_message("Scrittura dei file .srt in corso")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(srt.compose(subtitles))

def merge_srt_files(srt_files_info, final_file_path):
    log_message("Merge dei file .srt in un unico file aggiustando gli Index e le sequenze temporali")
    all_subtitles = []
    next_start_index = 1
    
    last_end_time = timedelta(0)  # Inizializza il tempo di fine dell'ultimo sottotitolo
    
    for file_info in srt_files_info:
        subtitles, _, _ = extract_and_clean_srt(file_info[0])
        
        # Aggiorna gli indici dei sottotitoli per la continuità
        for subtitle in subtitles:
            subtitle.index = next_start_index
            next_start_index += 1
        
        # Aggiungi i sottotitoli alla lista complessiva
        all_subtitles.extend(subtitles)
        
        # Aggiorna il tempo di inizio di tutti i sottotitoli nel file corrente
        for subtitle in subtitles:
            subtitle.start += last_end_time
            subtitle.end += last_end_time
        
        # Aggiorna il tempo di fine dell'ultimo sottotitolo
        last_end_time = subtitles[-1].end
    
    # Scrivi tutti i sottotitoli nel file finale
    write_subtitles_to_file(all_subtitles, final_file_path)

    print(f"Il file '{final_file_path}' è stato generato correttamente")



def get_srt_files(directory):
    log_message("Lettura dei file .srt in corso...")
    srt_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".srt") and "_part" in f]
    # Ordina i file .srt in base al numero di parte nel loro nome
    srt_files.sort(key=lambda x: int(re.search(r'_part(\d+)\.srt$', x).group(1)))
    return srt_files


################## Implementazione Funzioni e Steps

# download del video e dell'audio
def scarica_audio(title, url):
    if title:
        check_and_delete_mp3(title)
    else:
        log_message("Impossibile procedere senza il titolo del video.")
        log_message("Operazione completata.")

    youtube_url = url
    mp3_file = download_audio(youtube_url)

    if mp3_file:
        log_message(f"File MP3 '{mp3_file}' creato con successo.")
    log_message("Operazione completata.")

# split dei file
def dividi_audio(title):
    mp3_file = title + ".mp3"
    audio_file = mp3_file
    audio = AudioSegment.from_mp3(audio_file)
    base_name = os.path.splitext(audio_file)[0]
    split_and_rename(audio, base_name)

# trascrizione dell'audio
def trascrivi_audio():
    transcribe_audio_files()

# unisci i sottotitoli in un unico file
def unisci_srt():
    directory = os.getcwd()
    srt_files = get_srt_files(directory)
    final_file_path = os.path.join(directory, "merged_subtitles.srt")

    srt_files_info = [(file_path, ) for file_path in srt_files]
    merge_srt_files(srt_files_info, final_file_path)

    print(f"Il file '{final_file_path} è stato generato correttamente'")

################## Implementazione dell'Interfaccia Utente ##################

def main():
    # Recupero dell'url del video per estrarre il titolo
    url = input("Inserisci l'URL del video di YouTube: ")
    title = get_video_title(url)

    if title:
        # Creazione della cartella utilizzando il titolo del video come nome
        folder_name = title.replace(" ", "_")  # Sostituisci gli spazi con underscore
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            log_message(f"Cartella '{folder_name}' creata con successo.")
        else:
            log_message(f"La cartella '{folder_name}' esiste già.")

        # Cambio directory di lavoro nella nuova cartella
        os.chdir(folder_name)
        log_message(f"Directory di lavoro cambiata in: {os.getcwd()}")

    print("YouTube .srt Toolkit V0.1b")
    while True:
        print("\nSeleziona l'operazione da eseguire:")
        print("1. Scarica audio")
        print("2. Dividi audio")
        print("3. Trascrivi audio")
        print("4. Unisci file SRT")
        print("9. Esegui tutto")
        print("0. Esci")
        scelta = input("> ")

        if scelta == "0":
            break
        elif scelta == "1":
            scarica_audio(title,url)
        elif scelta == "2":
            dividi_audio(title)
        elif scelta == "3":
            trascrivi_audio()
        elif scelta == "4":
            unisci_srt()
        elif scelta == "9":
            scarica_audio(title,url)
            dividi_audio(title)
            trascrivi_audio()
            unisci_srt()
        pass

if __name__ == "__main__":
    main()
