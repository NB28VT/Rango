from django.template import RequestContext
from django.shortcuts import render_to_response

from rango.models import Category, Page



def index(request):
   context = RequestContext(request)
   #query database for a list of all categories currently stored
   #order by number of likes in descending order.
   #retrieve the top 5 only, or less if less than 5
   #place the list in our context_dict dictionary which will be
   #passed to template engine
   category_list = Category.objects.order_by('-likes')[:5]
   page_list = Page.objects.order_by('-views')[:5]
   context_dict = {'categories': category_list, 'pages': page_list}
   
   
   #The following two lines are new.
   # We loop through each category returned, and create a URL attribute.
   #This attribute stores an encoded URl (e.g. spaces replaced with underscores)
   for category in category_list:
       category.url = category.name.replace(' ','_')

 
       
       
   
   
   # Return a rendered response to send to the client.
   # We make use of the shortcut function to make our lives easier.
   # Note that the first parameter is the function we wish to use
   return render_to_response('rango/index.html', context_dict, context)
   
    
def about(request):
   context = RequestContext(request)
   context_dict = {'boldmessage': "I am the bold font from the about context"}
   return render_to_response('rango/about.html', context_dict, context)
   
   

   
   
   
   
def category(request, category_name_url):
    #request our context from the request passed to us
    context = RequestContext(request)
       
       #change underscores in the category name to spaces.
       #URLs don't handle spaces well, so we encode them as underscores
       #We can simply replace them with spaces again to get the name.
       
    category_name = category_name_url.replace('_', ' ')
       
       #create a context dictionary which we can pass to the template rendering engine.
       #We start by containing the name of the category passed by the user.
    context_dict = {'category_name': category_name}
       
    try:
           #Can we find a category with the given name?
           #If we can't, the .get() method raises a DoesNotExist exception.
           #So the .get() method retruns one model instance or raises an exception
           category = Category.objects.get(name=category_name)
           
           #Retrieve all of the associated pages.
           #Note that filter returns >= 1 model instance
           pages = Page.objects.filter(category=category)
           
           #Adds our results list to the template context under name pages
           context_dict['pages']=pages
           
           #We'll also add this category object from the database to the context dic
           #We'll use this in the template to verify that the category exists
           context_dict['category']= category
        
    except Category.DoesNotExist:
            #We get here if we didn't find the specificied category.
            #Don't do anything - the template displays the "no category" message for us 
            pass
        #Go render the response and return it to the client.
        
    return render_to_response ('rango/category.html', context_dict, context)
        
        
        

           
       
       