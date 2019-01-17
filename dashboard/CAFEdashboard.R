library(shiny)

source("/Users/jokedurnez/Documents/accounts/CAFE/CAFE/time_use_diary/TUD_analysis.R")

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

ui <- navbarPage(
  
  tabPanel(
    "Preprocessed",
    sidebarLayout(
      sidebarPanel(
        downloadButton("download_preprocessed", "Download")
      ),
      mainPanel(
        "Preprocessed data",
          dataTableOutput(outputId = "preprocessed")
      )
    )
  ),
  
  tabPanel(
    "Summarised",
    sidebarLayout(
      sidebarPanel(
        downloadButton("download_summarised", "Download")
      ),
      mainPanel(
        "Preprocessed data",
        dataTableOutput(outputId = "summarised")
      )
    )
  ),
    
  tabPanel(
    "Histograms",
    sidebarLayout(
      sidebarPanel(
        selectInput(inputId = 'columnname', choices = names(TUD_summarised), label='Column')
        
      ),
      mainPanel(
        plotOutput(outputId = "histogram")
      )
    )
  ),
  
  tags$head(
    tags$style(
      HTML(
        '
        .navbar {
        background-color:purple;
        color: white!important;
        border-color:white;
        height: 60px;
        }
        .navbar-brand {
        color:white!important;
        }
       .navbar-nav li a:hover, .navbar-nav > .active > a{
        color: black !important ;
        
        background-color: white !important;
        }
        '
      )
    )
  ),
  
  title = "CAFE"
  
)

server <- function(input, output, session) {
  
  output$preprocessed <- renderDataTable({
    as_tibble(TUD_preprocessed)
  })
  
  output$summarised <- renderDataTable({
    as_tibble(TUD_summarised)
  })
  
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