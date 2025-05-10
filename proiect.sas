/* /home/u64228609 */


/* Cerinta 1 */
DATA students;
   INFILE '/home/u64228609/student_habits_performance.csv' DLM=',' FIRSTOBS=2;
   INPUT student_id $ age gender $ study_hours_per_day social_media_hours netflix_hours
         part_time_job $ attendance_percentage sleep_hours diet_quality $
         exercise_frequency parental_education_level $ internet_quality $
         mental_health_rating extracurricular_participation $ exam_score;
RUN;


PROC PRINT DATA=students (OBS=10);
RUN;

/* Statistici descriptive */
PROC MEANS DATA=students;
   VAR age study_hours_per_day social_media_hours netflix_hours 
       attendance_percentage sleep_hours exercise_frequency 
       mental_health_rating exam_score;
RUN;


/* CERINTA 2 */
PROC FORMAT;
   VALUE scorefmt
      0-<60 = 'Insuficient'
      60-<70 = 'Satisfăcător'
      70-<80 = 'Bine'
      80-<90 = 'Foarte Bine'
      90-100 = 'Excelent';
   
   VALUE studyfmt
      0-<2 = 'Foarte Puțin'
      2-<4 = 'Puțin'
      4-<6 = 'Moderat'
      6-<8 = 'Mult'
      8-10 = 'Foarte Mult';
      
   VALUE sleepfmt
      0-<6 = 'Insuficient'
      6-<7 = 'Suboptimal'
      7-<9 = 'Optim'
      9-12 = 'Extins';
      
   VALUE mediafmt
      0-<1 = 'Minim'
      1-<3 = 'Moderat'
      3-<5 = 'Ridicat'
      5-high = 'Excesiv';
RUN;


/* Aplicarea formatelor și afișarea datelor formatate */
DATA students_formatted;
   SET students;
   FORMAT exam_score scorefmt. study_hours_per_day studyfmt. 
          sleep_hours sleepfmt. social_media_hours mediafmt.;
RUN;

/* Afișarea datelor cu formatele aplicate */
PROC PRINT DATA=students_formatted (OBS=15);
   VAR student_id age gender study_hours_per_day social_media_hours 
       sleep_hours exam_score;
RUN;

/* Tabel de frecvență pentru categoriile de performanță */
PROC FREQ DATA=students_formatted;
   TABLES exam_score / NOCUM;
RUN;

/* Tabel de contingență pentru relația dintre categoriile de studiu și performanță */
PROC FREQ DATA=students_formatted;
   TABLES study_hours_per_day * exam_score / NOROW NOCOL NOPCT;
RUN;


/* Cerinta 3 */

/* Selecția studenților cu performanțe deosebite și obiceiuri de studiu exemplare */
DATA high_performers;
   SET students;
   WHERE exam_score > 85 AND study_hours_per_day > 5 AND attendance_percentage > 90;
RUN;

/* Afișarea studenților cu performanțe deosebite */
PROC PRINT DATA=high_performers;
   VAR student_id gender study_hours_per_day attendance_percentage 
       sleep_hours mental_health_rating exam_score;
RUN;

/* Procesare condițională pentru evaluarea echilibrului între studiu și relaxare */
DATA student_balance;
   SET students;
   
   /* Calcularea timpului total petrecut pe activități digitale */
   digital_time = social_media_hours + netflix_hours;
   
   /* Evaluarea echilibrului între studiu și relaxare */
   IF study_hours_per_day > 0 THEN
      study_to_leisure_ratio = study_hours_per_day / MAX(digital_time, 0.1);
   ELSE
      study_to_leisure_ratio = 0;
   
   /* Clasificarea echilibrului */
   IF study_to_leisure_ratio < 0.5 THEN balance_category = 'Dezechilibrat spre relaxare';
   ELSE IF study_to_leisure_ratio < 1 THEN balance_category = 'Relativ echilibrat';
   ELSE IF study_to_leisure_ratio < 2 THEN balance_category = 'Echilibrat';
   ELSE IF study_to_leisure_ratio < 4 THEN balance_category = 'Focusat pe studiu';
   ELSE balance_category = 'Foarte focusat pe studiu';
   
   /* Înlocuirea valorilor lipsă pentru calitatea dietei */
   IF diet_quality = ' ' THEN DO;
      diet_quality = 'Medie';
      imputed_diet = 1;
   END;
   ELSE imputed_diet = 0;
RUN;

/* Afișarea distribuției categoriilor de echilibru */
PROC FREQ DATA=student_balance;
   TABLES balance_category / NOCUM;
RUN;

/* Analiza performanței în funcție de categoria de echilibru */
PROC MEANS DATA=student_balance;
   CLASS balance_category;
   VAR exam_score;
RUN;

/* Tratarea valorilor extreme pentru orele de studiu */
DATA students_cleaned;
   SET students;
   
   /* Identificarea și ajustarea valorilor extreme */
   IF study_hours_per_day > 12 THEN DO;
      original_study_hours = study_hours_per_day;
      study_hours_per_day = 12;  /* Plafonare la o valoare rezonabilă */
      adjusted = 1;
   END;
   ELSE adjusted = 0;
   
   /* Calcularea scorului de "eficiență a studiului" */
   IF study_hours_per_day > 0 THEN
      study_efficiency = exam_score / study_hours_per_day;
   ELSE
      study_efficiency = .;  /* Valoare lipsă pentru diviziunea la zero */
RUN;

/* Afișarea statisticilor descriptive pentru eficiența studiului */
PROC MEANS DATA=students_cleaned;
   VAR study_efficiency;
RUN;


/* Cerinta 4 */
/* Crearea de două subseturi de date pentru demonstrarea combinării */
DATA students_high_performers students_low_performers;
   SET students;
   IF exam_score >= 80 THEN OUTPUT students_high_performers;
   ELSE OUTPUT students_low_performers;
RUN;

/* Afișarea numărului de observații în fiecare subset */
PROC SQL;
   SELECT COUNT(*) AS HighPerformers FROM students_high_performers;
   SELECT COUNT(*) AS LowPerformers FROM students_low_performers;
QUIT;

/* Combinarea seturilor de date folosind procedura SET */
DATA students_combined_sas;
   SET students_high_performers students_low_performers;
RUN;

/* Afișarea primelor 10 observații din setul de date combinat */
PROC PRINT DATA=students_combined_sas (OBS=10);
RUN;

/* Combinarea seturilor de date folosind SQL */
PROC SQL;
   CREATE TABLE students_combined_sql AS
   SELECT * FROM students_high_performers
   UNION ALL
   SELECT * FROM students_low_performers;
QUIT;

/* Verificarea că cele două metode au produs aceleași rezultate */
PROC COMPARE BASE=students_combined_sas COMPARE=students_combined_sql;
RUN;

/* Combinarea cu LEFT JOIN pentru a adăuga informații despre stresul academic */
/* Mai întâi creăm un tabel cu niveluri estimate de stres bazate pe diverse variabile */
DATA student_stress;
   SET students;
   /* Calculăm un scor de stres simplu bazat pe orele de studiu, timpul petrecut pe social media și prezență */
   stress_score = (study_hours_per_day * 2) + social_media_hours - (attendance_percentage / 10) - (sleep_hours / 2);
   
   /* Clasificăm nivelul de stres */
   IF stress_score < 0 THEN stress_level = 'Scăzut';
   ELSE IF stress_score < 10 THEN stress_level = 'Moderat';
   ELSE IF stress_score < 20 THEN stress_level = 'Ridicat';
   ELSE stress_level = 'Foarte ridicat';
   
   KEEP student_id stress_level stress_score;
RUN;

/* Combinăm setul original cu informațiile despre stres folosind SQL */
PROC SQL;
   CREATE TABLE students_with_stress AS
   SELECT a.*, b.stress_level, b.stress_score
   FROM students AS a
   LEFT JOIN student_stress AS b
   ON a.student_id = b.student_id;
QUIT;

/* Analizăm relația dintre nivelul de stres și performanța academică */
PROC MEANS DATA=students_with_stress;
   CLASS stress_level;
   VAR exam_score;
RUN;

/* Realizăm o analiză de corelație între scorul de stres și scorul la examene */
PROC CORR DATA=students_with_stress;
   VAR stress_score exam_score;
RUN;

/* Cerinta 5 */

/* Generarea unui raport detaliat despre performanța academică pe diverse categorii */
/* Analiza performanței în funcție de gen */
PROC MEANS DATA=students;
   CLASS gender;
   VAR exam_score;
   TITLE "Performanța academică în funcție de gen";
RUN;

/* Analiza performanței în funcție de participarea la activități extracurriculare */
PROC MEANS DATA=students;
   CLASS extracurricular_participation;
   VAR exam_score;
   TITLE "Performanța academică în funcție de participarea extracurriculară";
RUN;

/* Analiza performanței în funcție de calitatea dietei */
PROC MEANS DATA=students;
   CLASS diet_quality;
   VAR exam_score;
   TITLE "Performanța academică în funcție de calitatea dietei";
RUN;

/* Analiza influenței sănătății mintale asupra performanței */
PROC MEANS DATA=students;
   CLASS mental_health_rating;
   VAR exam_score study_hours_per_day attendance_percentage;
   TITLE "Influența sănătății mintale asupra performanței academice";
RUN;

/* Raport sumativ pentru toate variabilele numerice */
PROC MEANS DATA=students;
   VAR age study_hours_per_day social_media_hours netflix_hours
       attendance_percentage sleep_hours exercise_frequency
       mental_health_rating exam_score;
   TITLE "Statistici descriptive pentru variabilele numerice";
RUN;

/* Analiza factorilor care prezic performanța ridicată */
PROC FREQ DATA=students;
   TABLES gender*exam_score / CHISQ;
   TITLE "Relația dintre gen și performanța academică";
RUN;

PROC FREQ DATA=students;
   TABLES diet_quality*exam_score / CHISQ;
   TITLE "Relația dintre calitatea dietei și performanța academică";
RUN;

PROC FREQ DATA=students;
   TABLES part_time_job*exam_score / CHISQ;
   TITLE "Relația dintre job-ul part-time și performanța academică";
RUN;

/* Raport despre distribuția scorurilor în funcție de educația părinților */
PROC MEANS DATA=students;
   CLASS parental_education_level;
   VAR exam_score;
   TITLE "Distribuția scorurilor în funcție de nivelul de educație al părinților";
RUN;

/* Cerinta 6 */
/* Creare grafic pentru relația dintre orele de studiu și scorurile la examene */
PROC SGPLOT DATA=students;
   TITLE "Relația dintre orele de studiu și scorurile la examene";
   REG X=study_hours_per_day Y=exam_score;
   SCATTER X=study_hours_per_day Y=exam_score / TRANSPARENCY=0.5;
   XAXIS LABEL="Ore de studiu pe zi";
   YAXIS LABEL="Scor la examene";
RUN;
TITLE;

/* Grafic pentru compararea scorurilor în funcție de calitatea dietei */
PROC SGPLOT DATA=students;
   TITLE "Scoruri la examene în funcție de calitatea dietei";
   VBOX exam_score / CATEGORY=diet_quality;
   XAXIS LABEL="Calitatea dietei";
   YAXIS LABEL="Scor la examene";
RUN;
TITLE;

/* Grafic pentru analiza efectului timpului petrecut pe rețele sociale */
PROC SGPLOT DATA=students;
   TITLE "Impactul timpului petrecut pe rețele sociale asupra performanței";
   REG X=social_media_hours Y=exam_score;
   SCATTER X=social_media_hours Y=exam_score / TRANSPARENCY=0.5;
   XAXIS LABEL="Ore pe rețele sociale pe zi";
   YAXIS LABEL="Scor la examene";
RUN;
TITLE;

/* Grafic pentru relația dintre prezență și performanță */
PROC SGPLOT DATA=students;
   TITLE "Relația dintre prezența la cursuri și performanța academică";
   REG X=attendance_percentage Y=exam_score;
   SCATTER X=attendance_percentage Y=exam_score / TRANSPARENCY=0.5;
   XAXIS LABEL="Procentaj prezență";
   YAXIS LABEL="Scor la examene";
RUN;
TITLE;

/* Grafic de bare pentru scorurile medii în funcție de participarea la activități extracurriculare */
PROC SGPLOT DATA=students;
   TITLE "Scoruri medii în funcție de participarea la activități extracurriculare";
   VBAR extracurricular_participation / RESPONSE=exam_score STAT=MEAN;
   YAXIS LABEL="Scor mediu la examene";
   XAXIS LABEL="Participare la activități extracurriculare";
RUN;
TITLE;

/* Histogramă pentru distribuția scorurilor la examene */
PROC SGPLOT DATA=students;
   TITLE "Distribuția scorurilor la examene";
   HISTOGRAM exam_score / BINWIDTH=5;
   DENSITY exam_score / TYPE=KERNEL;
   XAXIS LABEL="Scor la examene";
   YAXIS LABEL="Frecvență";
RUN;
TITLE;

/* Grafic de tip bubble pentru relația dintre studiu, somn și performanță */
PROC SGPLOT DATA=students;
   TITLE "Relația dintre studiu, somn și performanță academică";
   BUBBLE X=study_hours_per_day Y=sleep_hours SIZE=exam_score;
   XAXIS LABEL="Ore de studiu pe zi";
   YAXIS LABEL="Ore de somn pe noapte";
RUN;
TITLE;