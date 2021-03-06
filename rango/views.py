from django.template import RequestContext
from django.shortcuts import render_to_response

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from datetime import datetime

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
  #for category in category_list:
     #category.url = category.name.replace(' ','_')      

  #use new function
  for category in category_list:
     encode_url(category)



  # NEW CODE ####
  # Obtain our Response object early so we can add cookie information.
  response = render_to_response('rango/index.html', context_dict, context)

  # Get the number of visits to the site.
  # We use the COOKIES.get() function to obtain the visits cookie.
  # If the cookie exists, the value returned is casted to an integer.
  # If the cookie doesn't exist, we default to zero and cast that.
  visits = int(request.COOKIES.get('visits', '0'))

  # Does the cookie last_visit exist?
  if 'last_visit' in request.COOKIES:
      # Yes it does! Get the cookie's value.
      last_visit = request.COOKIES['last_visit']
      # Cast the value to a Python date/time object.
      last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

      # If it's been more than a day since the last visit...
      if (datetime.now() - last_visit_time).days > 0:
          # ...reassign the value of the cookie to +1 of what it was before...
          response.set_cookie('visits', visits+1)
          # ...and update the last visit cookie, too.
          response.set_cookie('last_visit', datetime.now())
  else:
      # Cookie last_visit doesn't exist, so create it to the current date/time.
      response.set_cookie('last_visit', datetime.now())

  # Return response back to the user, updating any cookies that need changed.
  return response
  #### END NEW CODE ####












       







   
def category(request, category_name_url):
    #request our context from the request passed to us
    context = RequestContext(request)
       
       #THIS FUNCTIONALITY WAS REMOVED. SEEE BELOW FOR NEW FUNCTION
       #change underscores in the category name to spaces.
       #URLs don't handle spaces well, so we encode them as underscores
       #We can simply replace them with spaces again to get the name.
       
    #category_name = category_name_url.replace('_', ' ')
     
    #NEW FUNCTION 
    category_name = decode_url(category_name_url) 
     
     
     
       
       #create a context dictionary which we can pass to the template rendering engine.
       #We start by containing the name of the category passed by the user.
    context_dict = {'category_name': category_name, 'category_name_url': category_name_url} 
       
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
        
   
   

 
 
def encode_url(category):
    category.url= category.name.replace(' ','_')
    
def decode_url(category_name_url):
    category_name = category_name_url.replace('_',' ') 
    return category_name
   
   
@login_required   
def add_category(request):
    #Get the context from the request
    context = RequestContext(request)
    
    # A HTTP Post?
    if request.method == 'POST':
           form = CategoryForm(request.POST)
           
           if form.is_valid():
               #Save the new category to the database
               form.save(commit=True)
        
               #Now call the index() view
               #The user will be shown the homepage
               return index(request)
           else:
               #The supplied form contained errors = just print them to the terminal
               print form.errors    
    else:
        #If the request was not a POST, display the form to enter details
        form=CategoryForm()
        
    #Bad form (or form details), no form supplied
    #Render the form with error message(if any)
    return render_to_response('rango/add_category.html', {'form':form}, context)        
               
   
@login_required   
def add_page(request, category_name_url):
    context=RequestContext(request)
    
    category_name = decode_url(category_name_url)
    
    if request.method=='POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            #This time we cannot commit straght away.
            #Not all fields are automatically populated!
            page = form.save(commit=False)
            
            #Retrieve the associated Category object so we can add it.
            #Wrap the code in a try block, check if the category exists
            
            try:
                cat = Category.objects.get(name=category_name)
                page.category=cat
            except Category.DoesNotExist:
                #If we get there the category does not exist.
                #Go back and render the add category form 
                return render_to_response('rango/add_category.html',{}, context)
                
            #Also, create a default value for a number of views
            page.views=0
            
            #With this, we can save our new model instance.
            page.save()    
            
            
            
            
            return category(request, category_name_url)
            
            
        else:
            print form.errors    
            
    else:
        form = PageForm()
        
        
    return render_to_response('rango/add_page.html', 
        {'category_name_url':category_name_url, 'category_name':category_name, 'form':form}, context)      
   
    
def about(request):
   context = RequestContext(request)
   context_dict = {'boldmessage': "I am the bold font from the about context"}
   return render_to_response('rango/about.html', context_dict, context)
   
   

   
def register(request):


    #Like before, get the resquest's context
    context = RequestContext(request)
    
    #A boolean value for telling the template whether the registration was successful.
    #Set to False initially. Code changes value to True when registration happens.
    registered = False
    
    #If it's a HTTP POST we're interested in processing form data.
    if request.method == 'POST':
        #Attempt to grab information from the raw form information.
        #Note that we make use of both the UserForm and UserProfileForm
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
       
        #If the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
                  #Save the users form to the database.
                  user = user_form.save()
     
                  #Now we hash the password with the set_password method
                  #Once hashed, we can update the user object.
                  user.set_password(user.password)
                  user.save()
     
                  #Now sort out the UserProfile instance.
                  #Since we need to set the user attribute ourselves, we set commit to false
                  #This delays saving the model until we're ready
                  profile = profile_form.save(commit=False)
                  profile.user = user
     
                  #Did the user provide a profile picture?
                  #If so, we need to get it from the input form
                  if 'picture' in request.FILES:
                      profile.picture = request.FILES['picture']
         
                  #Now we save the UserProfile model instance
                  profile.save()
     
                  #Update our variable to the template registration is completed
                  registered = True
     
        #Invalid form or forms - mistakes or something else?
        # Print problems to the terminal
        # They'll also be shown to the user.

        else:
            print user_form.errors, profile_form.errors
       
      
   
   
        

    #No a HTTP POST, so we render our form using two ModelForm instances
    #These forms will be blank, ready for user input
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    #Returtn the template depending on the context.
    return render_to_response(
        'rango/register.html',
        {'user_form':user_form, 'profile_form': profile_form, 'registered':registered},
        context)              


        
def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('rango/login.html', {}, context)
       
        
@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text")        
                        
def user_logout(request):
    #Since we know the user is logged in, we can just log them out
    logout(request)
    
    #take the user back to the homepage.
    return HttpResponseRedirect('/rango/')
                    
                
                
                
                
                
         

           
       
       