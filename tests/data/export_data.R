#!/usr/bin/Rscript
library(LDAvis)
library(LDAvisData)
# RJSONIO did not roundtrip cleanly so it was annoying to use
library(jsonlite)

export <- function(data, name, out.dir='.') {
    cat(paste0('Exporting ', name, '...\n'))
    input <- jsonlite::toJSON(data, digits=50)
    input.name <- paste0(name, "_input.json")
    cat(input, file = file.path(out.dir, input.name))

    # roundtrip the JSON so both libraries are using the same precision
    data <- jsonlite::fromJSON(input)

    output <- createJSON(data$phi, data$theta, data$doc.length, data$vocab, data$term.frequency)
    output.name <- paste0(name, "_output.json")
    cat(output, file = file.path(out.dir, output.name))
    cat(paste0(input.name, ' and ', output.name, ' have been written.\n'))
}


#export(AP, 'ap')
#export(Jeopardy, 'jeopardy')
export(MovieReviews, 'movie_reviews')
