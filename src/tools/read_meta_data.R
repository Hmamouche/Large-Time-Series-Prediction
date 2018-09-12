# Author: Youssef Hmamouche

## elimination space funtion
trim <- function (x) gsub("^\\s+|\\s+$", "", x)

## read metadata from a file
read_meta_data <- function (data_dir)
{
    meta_data = list()

    command = paste0 ('awk /^#/ ',data_dir)
    dat <- system(command,  intern = TRUE)

    file_name_split = strsplit(data_dir, "/")[[1]]
    data_name = file_name_split[length(file_name_split)]
    meta_data$data_name = gsub(".csv", "",data_name, fixed=TRUE)

    datNamed <- read.table(text=gsub("^# *", "",gsub(" +", "",dat)), row.names = 1, sep=";",header=FALSE, fill = TRUE)

    meta_data$lag_p = strtoi(datNamed["lag_parameter","V2"])
    meta_data$horizon = strtoi(datNamed["horizon","V2"])
    meta_data$nbre_predictions = strtoi(datNamed["number_predictions","V2"])
    meta_data$max_attributes = strtoi(datNamed["max_attributes",1])

    meta_data$description = toString(datNamed["description",1])
    meta_data$target_names = datNamed["predict",]
    meta_data$target_names = meta_data$target_names[!is.na(meta_data$target_names)]
    
    meta_data$prediction_type = datNamed["prediction_type",1]

    if(is.na(meta_data$horizon))
        meta_data$horizon = 1

    if(is.na(meta_data$lag_p))
        meta_data$lag_p = 0

    if(is.na(meta_data$nbre_predictions))
        meta_data$nbre_predictions = 0

    return (meta_data)

}
