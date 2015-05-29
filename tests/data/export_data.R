#!/usr/bin/Rscript

ensure.packages <- function(packages) {
  packages.not.installed <- Filter(function(p) !(p %in% installed.packages()), packages)
  if(length(packages.not.installed) > 0) {
    install.packages(packages.not.installed, dep = T)
  }}

ensure.packages(c('LDAvis', 'LDAvisData', 'jsonlite'))

library(LDAvis)
library(LDAvisData)
# RJSONIO did not roundtrip cleanly so it was annoying to use
library(jsonlite)

export <- function(data, name, out.dir='.') {
    input.name <- paste0(name, "_input.json")
    if(!file.exists(input.name))
    {
        cat(paste0('Exporting ', name, '...\n'))
        input <- jsonlite::toJSON(data, digits=50)
        cat(input, file = file.path(out.dir, input.name))
    }

    output.name <- paste0(name, "_output.json")
    if(!file.exists(output.name))
    {
        # roundtrip the JSON so both libraries are using the same precision
        data <- jsonlite::fromJSON(input)
        output <- createJSON(data$phi, data$theta, data$doc.length, data$vocab, data$term.frequency)
        cat(output, file = file.path(out.dir, output.name))
        cat(paste0(input.name, ' and ', output.name, ' have been written.\n'))
    }
}


export(AP, 'ap')
export(Jeopardy, 'jeopardy')
export(MovieReviews, 'movie_reviews')
