library(shiny)
library(shinydashboard)
library(GGally)

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

if (interactive()) {
  
  ui <- dashboardPage(
  
    skin = "black",
    
    dashboardHeader(
      title = tags$a(href="http://www.openlattice.com", div(img(src='logo.png',height=30), "CAFE analytics dashboard")),
      titleWidth = 600
      ),
    
    dashboardSidebar(
      sidebarMenu(
        menuItem("Preprocessed data", tabName = "preprocessed"),
        menuItem("Summary data", tabName = "summarised"),
        menuItem("Histograms", tabName = "histograms"),
        menuItem("Cross-Plots", tabName = "cross-plots")
      )
    ),
    
    dashboardBody(
      tags$head(
        tags$link(rel="stylesheet", type="text/css", href="custom.css")
        ),
      tabItems(
        tabItem(
          "preprocessed",
          fluidRow(
            box(
              width = 12, 
              column(12, align="center", downloadButton("download_preprocessed", "Download"))
            )
          ),
          fluidRow(
            box(
              width = 12, solidHeader = TRUE,
              title = "Preprocessed data",
              dataTableOutput(outputId = "preprocessed")
            )
          )
        ),
        
        tabItem(
          "summarised",
          fluidRow(
            box(
              width = 12, 
              column(12, align="center", downloadButton("download_summarised", "Download"))
            )
          ),
          fluidRow(
            box(
              width = 12, solidHeader = TRUE,
              title = "Summarised data",
              dataTableOutput(outputId = "summarised")
            )
          )
        ),
  
        tabItem(
          "histograms",
          fluidRow(
            box(
              width = 12,
              title = "Select column",
              selectInput(inputId = 'hist_column', choices = numcols, label='Column')
            )
          ),
          fluidRow(
            box(
              width = 12, solidHeader = TRUE,
              title = "Histogram",
              plotOutput(outputId = "histogram")
            )
          )
        ),
        
        
        tabItem(
          "cross-plots",
          fluidRow(
            column(
              width = 4,
              box(
                width = 12,solidHeader = TRUE,
                title = "Select column",
                checkboxGroupInput(
                  "cross_columns", 
                  "Choose columns:",
                  choiceNames = as.list(numcols),
                  choiceValues = as.list(numcols)
                )
              )
            ),
            column(
              width = 8,
              box(
                width = 12, solidHeader = TRUE,
                title = "Cross-plot",
                plotOutput("crossplot")
              )
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
      ggplot(
        TUD_summarised,
        aes_string(x = input$hist_column)
      ) +
        geom_histogram(
          binwidth = 1,
          fill = "#4c14c4"
          )
    })
   
    output$crossplot <- renderPlot({
      if (length(input$cross_columns) > 0){
        ggpairs(
          TUD_summarised[,input$cross_columns],
          color = "black",
          diag = list(continuous = wrap("densityDiag", fill = "#4c14c4")),
          lower = list(continuous=wrap("smooth", colour="#4c14c4"))
        )
      }
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
}
shinyApp(ui, server)