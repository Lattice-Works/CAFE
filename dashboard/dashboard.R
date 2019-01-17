library(shiny)
library(shinydashboard)

source("pipelines/time_use_diary.R")

# read in data
TUfile <-
  "/Users/jokedurnez/Downloads/Time use diary set up and analysis/GU TUD 5Oct2018 Numeric.csv"

TUD_preprocessed <- TUfile %>%
  read_TU() %>%
  clean_TUD() %>%
  preprocess_TUD()

TUD_summarised <- TUD_preprocessed %>%
  summarise_TUD()

numcols <- names(dplyr::select_if(TUD_summarised,is.numeric))

ui <- dashboardPage(
  
  skin = "black",
  
  dashboardHeader(title = tags$a(href="http://www.openlattice.com", tags$img(src='logo.png',height=30))),
  
  dashboardSidebar(
    sidebarMenu(
      menuItem("Preprocessed data", tabName = "preprocessed"),
      menuItem("Summary data", tabName = "summarised"),
      menuItem("Visualisations", tabName = "visualisations")
    )
  ),
  
  dashboardBody(
    tags$head(tags$link(rel="stylesheet", type="text/css", href="custom.css")),
    tabItems(
      tabItem(
        "preprocessed",
        fluidRow(
          box(
            width = 8, 
            column(12, align="center", downloadButton("download_preprocessed", "Download"))
          )
        ),
        fluidRow(
          box(
            width = 8, solidHeader = TRUE,
            title = "Preprocessed data",
            dataTableOutput(outputId = "preprocessed")
          )
        )
      ),
      
      tabItem(
        "summarised",
        fluidRow(
          box(
            width = 8, 
            column(12, align="center", downloadButton("download_summarised", "Download"))
          )
        ),
        fluidRow(
          box(
            width = 8, solidHeader = TRUE,
            title = "Summarised data",
            dataTableOutput(outputId = "summarised")
          )
        )
      ),

      tabItem(
        "visualisations",
        fluidRow(
          box(
            width = 8,
            title = "Select column",
            selectInput(inputId = 'columnname', choices = numcols, label='Column')
          )
        ),
        fluidRow(
          box(
            width = 8, solidHeader = TRUE,
            title = "Summarised data",
            plotOutput(outputId = "histogram")
          )
        )
      )
    )
  )
)

server <- function(input, output, session) {
  
  output$preprocessed <- renderDataTable({
    as_tibble(TUD_preprocessed)
  },
  options = list(scrollX = TRUE)
  )
  
  output$summarised <- renderDataTable({
    as_tibble(TUD_summarised)
  },
  options = list(scrollX = TRUE)
  )
  
  output$histogram <- renderPlot({
    TUD_summarised %>% pull(input$columnname) %>% hist()
  })
  
  output$download_preprocessed <- downloadHandler(
    filename = "CAFE_TUD_preprocessed.csv",
    content = function(file) {
      write.csv(TUD_preprocessed, file, row.names = FALSE)
    }
  )

  output$download_summarised <- downloadHandler(
    filename = "CAFE_TUD_summarised.csv",
    content = function(file) {
      write.csv(TUD_summarised, file, row.names = FALSE)
    }
  )
  
  
  
}

shinyApp(ui, server)