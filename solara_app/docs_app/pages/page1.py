import solara


@solara.component
def page1():
    solara.Title("welcome page")
    with solara.Card("Home"):
        solara.Markdown("""
| Column 1 Header | Column 2 Header |
|-----------------|-----------------|
| Row 1, Column 1 | Row 1, Column 2 |
| Row 2, Column 1 | Row 2, Column 2 |
| Row 3, Column 1 | Row 3, Column 2 |


                        """)      



@solara.component
def page2():
    solara.Title("second page")
    with solara.Card("Background"):
        solara.Markdown("Page 1 is the best")      


@solara.component
def page3():
    solara.Title("third page")
    with solara.Card("Technology"):
        solara.Markdown("Page 1 is the best")      



@solara.component
def page4():
    solara.Title("fourth page")
    with solara.Card("Data Sources"):
        solara.Markdown("Page 1 is the best")      


#image_path="/static/public/gefs_20231121_06.pdf"


@solara.component
def page5():
    #iframe_html = "<iframe src='/static/public/gefs_20231121_06.pdf' style='width:90%; height:70vh; border:none;'></iframe>"
    iframe_html = """
     <div style='display: flex; justify-content: center; align-items: center; height: 70vh;'>
        <iframe src='/static/public/sample.pdf' style='width:90%; height:70vh; border:none;'></iframe>
     </div>""" 
    #with solara.VBox() as main:
    with solara.Card("GEFS Forecast"):
        solara.HTML(tag="div", unsafe_innerHTML=iframe_html)
        #return main
@solara.component
def page6():
    solara.Title("sixth page")
    with solara.Card("Data Sources"):
        #hvexplorer = df.hvplot.explorer()
        #hvexplorer
        #df.hvplot.scatter(x='bill_length_mm', y='bill_depth_mm', by='species')
        #solara.display(plot_widget)
        panel_html = """
     <div style='display: flex; justify-content: center; align-items: center; height: 70vh;'>
        <iframe src="ploomberlink-panel-app" style='width:90%; height:70vh; border:none;'></iframe>
     </div>""" 
    #with solara.VBox() as main:
        solara.HTML(tag="hvdiv", unsafe_innerHTML=panel_html)


      



routes = [
    solara.Route(path="/", component=page1, label="home"),
    solara.Route(path="background", component=page2, label="page1"),
    solara.Route(path="tech", component=page3, label="page2"),
    solara.Route(path="data-src", component=page4, label="page3"),
    solara.Route(path="test0", component=page5, label="page4"),
    solara.Route(path="test1", component=page6, label="page5")


]
