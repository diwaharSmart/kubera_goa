from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.urls import reverse
from django.contrib import messages
from django.core import serializers
import json
from decimal import Decimal

def cancel_order(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        if order.order_status=="accepted":
            return redirect('admin:KuberaApp_order_change', order_id)  
        # Implement your cancellation logic here
        # For example, you could set order_status to 'cancelled'
        order.order_status = 'cancelled'
        order.ticket_set.all().delete()
        order.save()
        
    except Order.DoesNotExist:
        pass  # Handle case where order doesn't exist

    return redirect('admin:KuberaApp_order_change', order_id)  # Redirect back to the order change page


def accept_orders_and_calculate_loot(request, draw_id):
    try:
        draw = Draw.objects.get(pk=draw_id)
        if draw.orders_accepted:
            messages.error(request, 'Orders Accepted Already')
            return redirect(reverse('admin:KuberaApp_draw_change', args=[draw_id]))
        
        draw.orders_accepted=True
        draw.save()
        orders = Order.objects.filter(draw=draw, order_status__in=['processing','accepted'])

        total_loot = sum(order.order_total for order in orders)

        # Update the loot_amount in the draw
        draw.loot_amount = total_loot
        draw.save()

        # Update the order statuses to 'accepted'
        orders.update(order_status='accepted')


        agents = draw.order_set.values_list('agent', flat=True).distinct()
        # print(agents)
        for agent in agents:
            try:
                agent_orders = Order.objects.filter(draw=draw, agent__id=agent, order_status='accepted')
                total_amount = sum(order.order_total for order in agent_orders)

                # agent = AgentUser.objects.get(user=agent_id)

                agent_collection,created = AgentCollectionBalance.objects.get_or_create(
                    agent=User.objects.get(id=agent),
                )

                agent_collection.total_collection_amount = agent_collection.total_collection_amount+Decimal(total_amount)
                agent_collection.save()
            except:
                pass
        messages.success(request, 'Agent collections generated successfully.')


        messages.success(request, 'All orders accepted and loot amount calculated successfully.')

    except Draw.DoesNotExist:
        messages.error(request, 'Draw not found.')

    return redirect(reverse('admin:KuberaApp_draw_change', args=[draw_id]))


def calculate_orders_and_calculate_loot(request, draw_id):
    try:
        draw = Draw.objects.get(pk=draw_id)
        orders = Order.objects.filter(draw=draw, order_status__in=['processing','accepted'])

        total_loot = sum(order.order_total for order in orders)

        # Update the loot_amount in the draw
        draw.loot_amount = total_loot
        draw.save()

        # Update the order statuses to 'accepted'
        # orders.update(order_status='accepted')

        messages.success(request, 'All orders accepted and loot amount calculated successfully.')

    except Draw.DoesNotExist:
        messages.error(request, 'Draw not found.')

    return redirect(reverse('admin:KuberaApp_draw_change', args=[draw_id]))

def get_item_by_pk(your_list, target_pk):
    for item in your_list:
        ticket_objs = item['ticket_obj']
        for ticket in ticket_objs:
            if ticket['pk'] == target_pk:
                return item
    return None

def generate_preview_result(request, draw_id):
    try:

        draw = Draw.objects.get(pk=draw_id)
        loot_amount = draw.loot_amount
        tickets = Ticket.objects.filter(draw__id = draw_id,order__order_status="accepted")
        
        
        calculated_amount = 0.00
        ticket_board_and_prices =[]
        for board in TicketPrice.objects.all():
            ticket_board_and_prices.append({"ticket_obj":serializers.serialize('json', [board]),"board_and_prices":serializers.serialize('json', board.boardwinngprice_set.all())})

        for item in ticket_board_and_prices:
            item['ticket_obj'] = json.loads(item['ticket_obj'])
            item['board_and_prices'] = json.loads(item['board_and_prices'])
        # print(ticket_board_and_prices)
        profit_analyisis = []
        for nn in range(10000):
            n = str(nn).zfill(4)
            n_splits={"d" : n[0],
                        "a" : n[1],
                        "b" : n[2],
                        "c" : n[3],
                        "ab" : n[1]+n[2],
                        "bc" : n[2]+n[3],
                        "ac" : n[1]+n[3],
                        "abc" : n[1]+n[2]+n[3],
                        "dabc": n
                    }
            
            winning_amount = 0.00
            for ticket in tickets:
                ticket_board_pk = ticket.board.pk
                result_item = get_item_by_pk(ticket_board_and_prices, ticket_board_pk)
                choosen_number = str(ticket.choosen_number).zfill(4)
                choosen_number_split = {
                    "dabc":choosen_number,
                    "a":choosen_number[1],
                    "b":choosen_number[2],
                    "c":choosen_number[3],
                    "ab":choosen_number[1]+choosen_number[2],
                    "bc":choosen_number[2]+choosen_number[3],
                    "ac":choosen_number[1]+choosen_number[3],
                    "abc":choosen_number[1:]
                }
                choosen_board = ticket.board.boardwinngprice_set.all()[0].board_name
                if choosen_board != "abc" or choosen_board != "dabc" :
                    choosen_number_split[choosen_board] = str(ticket.choosen_number)
                if result_item:
                    # print("Item found:")
                    # print(result_item)
                    board_list = result_item["board_and_prices"]
                    for board_item in board_list:
                        
                        b_name = board_item["fields"]["board_name"]
                        if choosen_number_split[b_name] == n_splits[b_name]:
                            am=float(board_item["fields"]["winning_price"])*ticket.quantity
                            winning_amount=winning_amount+am
                            break
                else:
                    print("Item not found.")

            profit_analyisis.append(
                {
                    "number":str(nn).zfill(4),
                    "settelment_amount":winning_amount,
                    "amount_recieved": draw.loot_amount
                }
            )
        
        data = []
        # print(profit_analyisis)
        for item in profit_analyisis:
            amount_received = item['amount_recieved']
            settlement_amount = item['settelment_amount']
            
            remaining_amount = amount_received - Decimal(settlement_amount)
            
            if amount_received != Decimal('0'):
                profit_percentage = (remaining_amount / amount_received) * Decimal('100')
            else:
                profit_percentage = Decimal('0')  # Handle division by zero
            
            item['remaining_amount'] = remaining_amount
            item['profit_percentage'] = int(profit_percentage)    
            data.append(item)
        
        unique_profit_percentages = set()
        filtered_data = []
        import random
        random.shuffle(data)
        for item in data:
            profit_percentage = item['profit_percentage']

            if profit_percentage not in unique_profit_percentages:
                unique_profit_percentages.add(profit_percentage)
                filtered_data.append(item)

        context = {
            'filtered_data': filtered_data,
            "draw_id":draw.id
        }
        return render(request, 'kuberaapp/kuberalotty.html', context)
    except Draw.DoesNotExist:
        messages.error(request, 'Draw not found.')

    return redirect(reverse('admin:KuberaApp_draw_change', args=[draw_id]))

def generate_result(request, draw_id,number):
    try:

        draw = Draw.objects.get(pk=draw_id)
        if draw.result_generated:
            return render(request, 'kuberaapp/failure.html')
        loot_amount = draw.loot_amount
        tickets = Ticket.objects.filter(draw__id = draw_id,order__order_status="accepted")
        
        
        calculated_amount = 0.00
        ticket_board_and_prices =[]
        for board in TicketPrice.objects.all():
            ticket_board_and_prices.append({"ticket_obj":serializers.serialize('json', [board]),"board_and_prices":serializers.serialize('json', board.boardwinngprice_set.all())})

        for item in ticket_board_and_prices:
            item['ticket_obj'] = json.loads(item['ticket_obj'])
            item['board_and_prices'] = json.loads(item['board_and_prices'])
        # print(ticket_board_and_prices)
        profit_analyisis = []
       
        n = str(number).zfill(4)
        n_splits={"d" : n[0],
                    "a" : n[1],
                    "b" : n[2],
                    "c" : n[3],
                    "ab" : n[1]+n[2],
                    "bc" : n[2]+n[3],
                    "ac" : n[1]+n[3],
                    "abc" : n[1]+n[2]+n[3],
                    "dabc": n
                }
        
        winning_amount = 0.00
        for ticket in tickets:
            ticket_board_pk = ticket.board.pk
            result_item = get_item_by_pk(ticket_board_and_prices, ticket_board_pk)
            choosen_number = str(ticket.choosen_number).zfill(4)
            choosen_number_split = {
                "dabc":choosen_number,
                "a":choosen_number[1],
                "b":choosen_number[2],
                "c":choosen_number[3],
                "ab":choosen_number[1]+choosen_number[2],
                "bc":choosen_number[2]+choosen_number[3],
                "ac":choosen_number[1]+choosen_number[3],
                "abc":choosen_number[1:]
            }
            choosen_board = ticket.board.boardwinngprice_set.all()[0].board_name
            if choosen_board != "abc" or choosen_board != "dabc" :
                choosen_number_split[choosen_board] = str(ticket.choosen_number)

            if result_item:
                # print("Item found:")
                # print(result_item)
                board_list = result_item["board_and_prices"]
                for board_item in board_list:
                    
                    b_name = board_item["fields"]["board_name"]
                    if choosen_number_split[b_name] == n_splits[b_name]:
                        am=float(board_item["fields"]["winning_price"])*ticket.quantity
                        
                        winning_amount=winning_amount+am
                        ticket.winner=True
                        ticket.winning_amount = am
                        ticket.save()
                        
                        break
            else:
                print("Item not found.")

        
        orders = Order.objects.filter(draw=draw,order_status="accepted")

        # Calculate and update winning amount for each order
        for order in orders:
            tickets = Ticket.objects.filter(order=order)
            winning_amount = sum(ticket.winning_amount for ticket in tickets)
            order.winning_amount = winning_amount
            order.save()        

        agent_users = User.objects.filter(user_type='agent')

        # Calculate and create AgentWinning objects for each agent
        for agent_user in agent_users:
            # Filter orders associated with the agent and the draw
            orders = Order.objects.filter(agent=agent_user, draw=draw,order_status="accepted")
            
            # Calculate total winning amount for the agent
            total_winning_amount = sum(order.winning_amount for order in orders)
            
            # Create or update AgentWinning object
            agent_winning, created = AgentWinning.objects.get_or_create(agent=agent_user, draw=draw)
            agent_winning.winning_amount = total_winning_amount
            agent_winning.save()


        draw.result_generated = True
        draw.released = True
        draw.result_number = int(number)
        draw.save()
            

            
        return render(request, 'kuberaapp/success.html')

    except Draw.DoesNotExist:
        messages.error(request, 'Draw not found.')

    return redirect(reverse('admin:KuberaApp_draw_change', args=[draw_id]))      

def home(request):
    # Retrieve active draws
    active_draws = Draw.objects.filter(is_active=True)

    context = {
        'active_draws': active_draws,
    }
    return render(request, 'kuberaapp/home.html', context)


def draws_list(request):
    active_draws = Draw.objects.all()
    context = {'active_draws': active_draws}
    return render(request, 'kuberaapp/results.html', context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Ticket

@login_required(login_url='login')
def view_tickets(request):
    user = request.user
    tickets = Ticket.objects.filter(customer=user)
    context = {'tickets': tickets}
    return render(request, 'kuberaapp/mytickets.html', context)



@login_required(login_url='login')
def view_orders(request):
    user = request.user
    orders = Order.objects.filter(customer=user)
    context = {'orders': orders}
    return render(request, 'kuberaapp/myorders.html', context)

@login_required(login_url='login')
def search_agent(request):
    # if request.user.is_supervisor:
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        
        if agent_exists(agent_id):
            return redirect(reverse('agent_search_success', kwargs={'agent_id': agent_id}))
        else:
            return redirect('search_agent')
    return render(request, 'kuberaapp/agent-search.html')
    # else:
    #     return redirect('home')

def agent_exists(agent_id):
    try:
        User.objects.filter(username=agent_id)
        return True
    except:
        return False  # Replace with your actual logic

@login_required(login_url='login') 
def agent_search_success(request, agent_id):
    user = get_object_or_404(User, username=agent_id)
    agent_collection_balance = get_object_or_404(AgentCollectionBalance, agent=user)
    agent_collection_amounts = AgentCollectionAmount.objects.filter(agent_collection=agent_collection_balance)

    total_collected_amount = sum(amount.amount_recieved for amount in agent_collection_amounts)
    remaining_balance = agent_collection_balance.total_collection_amount - total_collected_amount

    last_10_collection_amounts = agent_collection_amounts.order_by('-collection_date')[:10]

    if request.method == 'POST':
        collected_amount = float(request.POST['amount'])
        if collected_amount > 0 and collected_amount <= remaining_balance:
            AgentCollectionAmount.objects.create(agent_collection=agent_collection_balance, amount_recieved=collected_amount)
            return redirect('agent_search_success', agent_id=agent_id)

    context = {
        'agent_id': agent_id,
        'first_name': user.first_name,
        'mobile_number': user.username,  # Adjust the attribute name based on your UserProfile model
        'collected_amount': total_collected_amount,
        'remaining_balance': remaining_balance,
        'last_10_collection_amounts': last_10_collection_amounts,
    }

    return render(request, 'kuberaapp/agent_search_success.html', context)




from .forms import DepositForm, UserRegistrationForm
from django.contrib.auth import login


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('home')  # Redirect to home page after successful registration
        else:
            # Check if the error is due to an existing mobile number
            
            return redirect('login')  # Redirect to home page after login
            

    else:
        form = UserRegistrationForm()
    return render(request, 'kuberaapp/register.html', {'form': form})



from django import forms

class MobileNumberLoginForm(forms.Form):
    mobile_number = forms.CharField(max_length=15)

def user_login(request):
    if request.method == 'POST':
        form = MobileNumberLoginForm(request.POST)
        if form.is_valid():
            mobile_number = form.cleaned_data['mobile_number']
            
            try:
                user = User.objects.get(username=mobile_number)
                
                # Log in the user
                login(request, user)
                return redirect('home')  # Redirect to home page after successful login
            except User.DoesNotExist:
                return redirect('register')  # User does not exist, handle this case as needed
    else:
        form = MobileNumberLoginForm()
    return render(request, 'kuberaapp/login.html', {'form': form})


def agent_list(request):
    agents = User.objects.filter(user_type="agent")  # Assuming you have a field 'is_agent' in User model to identify agents
    return render(request, 'kuberaapp/agent_list.html', {'agents': agents})


def agent_settlement(request, username):
    agent = User.objects.get(username=username)
    agent_winnings = AgentWinning.objects.filter(agent=agent, settled=False)
    
    total_winning_amount = agent_winnings.aggregate(total_amount=models.Sum('winning_amount'))['total_amount']
    
    return render(request, 'kuberaapp/agent_winning.html', {'agent': agent, 'total_winning_amount': total_winning_amount, 'agent_winnings': agent_winnings})


def settle_winnings(request, username):
    agent = User.objects.get(username=username)
    agent_winnings = AgentWinning.objects.filter(agent=agent, settled=False)
    order=Order.objects.filter(agent=agent)
    order.order_status = 'settled'
    order.save()
    tickets = Ticket.objects.filter(order=order)
    for ticket in tickets:
        ticket.settled=True
        ticket.save()
    
    # Update all un-settled winnings for the agent
    agent_winnings.update(settled=True)
    
    return redirect('agent_list')

from .models import OrderCreation
from .forms import OrderCreationForm
from django import forms

from django.forms import formset_factory
@login_required(login_url='login') 
def create_order(request,draw_id):
    OrderCreationFormSet = formset_factory(OrderCreationForm, extra=1)

    if request.method == 'POST':
        draw = Draw.objects.get(pk=draw_id)
        formset = OrderCreationFormSet(request.POST)
        order = Order.objects.create(customer=request.user,draw=draw,
                    order_status="pending")
        if formset.is_valid():
            for form in formset:
                # Save each form individually
                
                numbers_text = form.cleaned_data['numbers']
                board = form.cleaned_data['board']

                    # Process the numbers_text and create OrderCreation instance
                    # ...
                items = numbers_text.split(',')
                # print("numbers",items)
                for item in items:
                    item_parts = item.strip()   # Split and remove spaces
                   
                     
                    choosen_number = int(item_parts)
                    quantity = 1
                    

                    # Calculate total_amount based on ticket value and quantity
                    total_amount = board.ticket_value * quantity

                    # Create a Ticket instance with calculated values
                    ticket = Ticket(
                        # agent=request.user,
                        draw=draw,
                        customer=request.user,
                        board=board,
                        choosen_number=choosen_number,
                        quantity=quantity,
                        total_price=total_amount,
                        order=order  # Set the order for the ticket
                    )
                    
                    ticket.save()
                            
                        
                order_total = sum(ticket.total_price for ticket in order.ticket_set.all())
                order.order_total = order_total
                order.save()

                order_creation = OrderCreation.objects.create(
                    order=order,
                    board=board,
                    numbers=numbers_text,
                )
               
                upi_address = WebsiteInfo.objects.all()[0].upi_id
                OrderApproval.objects.create(
                    order=order,
                    user = request.user,
                    # transaction_id =reference_id,
                    upi_address = upi_address
                )
                order.order_status="not_approved"
                order.save()
                # You can process the data further if needed
            return redirect('order_preview', order_id=order.pk)  # Redirect to a success page
    else:
        formset = OrderCreationFormSet()

    context = {'formset': formset}
    return render(request, 'kuberaapp/create_order.html', context)
    

from django.template.loader import render_to_string
from django.http import HttpResponse
def create_formset(request):
    form = OrderCreationForm(prefix=f'form-{request.POST["form-TOTAL_FORMS"]}')
    context = {'form': form}
    return HttpResponse(render_to_string('kuberaapp/_formset.html', context))


    
@login_required(login_url='login')
def wallet(request):
    user = request.user
    customer_balance,created = CustomerBalance.objects.get_or_create(user=user)
    balance = customer_balance.balance

    # Fetch the transaction history
    transactions = CustomerBalanceHistory.objects.filter(wallet=customer_balance).order_by('-transaction_date')

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            transaction_id = form.cleaned_data['transaction_id']
            # upi_address = form.cleaned_data['upi_address']

            # Create a new transaction history record
            webinfo = WebsiteInfo.objects.all()[0]
            try:
                CustomerBalanceHistory.objects.create(
                    wallet=customer_balance,
                    amount=amount,
                    transaction_approved=False,
                    transaction_id=transaction_id,
                    upi_address=webinfo.upi_id,
                    # unique_id  = str(transaction_id)+str(webinfo.upi_id)
                )
            except:
                return redirect('wallet')

            # You can redirect to a success page or reload the wallet page
            return redirect('wallet')
    else:
        form = DepositForm()

    context = {
        'balance': balance,
        'transactions': transactions,
        'form': form
    }

    return render(request, 'kuberaapp/wallet.html', context)

@login_required(login_url='login')
def order_preview(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    context = {'order': order}
    if request.method == "POST":
        try:
            # reference_id = request.POST.get("reference_id")
            amount = request.POST.get("amount")
            upi_address = request.POST.get("upi_address")
            OrderApproval.objects.create(
                order=order,
                user = request.user,
                # transaction_id =reference_id,
                upi_address = upi_address
            )
            order.order_status="not_approved"
            order.save()
            print("aaaaaa")
            return redirect('view_orders')
        except:
            return redirect('view_orders')

    
    return render(request, 'kuberaapp/preview-order.html', context)


def checkout(request, order_id,status):
    try:
        order = Order.objects.get(pk=order_id)
        order.order_status = status
        order.save()

        return redirect('view_orders')
    
    except Order.DoesNotExist:
        return redirect('home')  # Order not found, redirect to home page

    

from .forms import BankInfoForm  # Import your BankInfoForm

@login_required(login_url='login')
def edit_bank_info(request):
    user = request.user

    if request.method == 'POST':
        form = BankInfoForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('edit_bank_info')
    else:
        form = BankInfoForm(instance=user)

    context = {'form': form}
    return render(request, 'kuberaapp/edit_bank_info.html', context)


def transaction_history(request):
    # Filter transactions with transaction_status set to 'pending'
    transactions = CustomerBalanceHistory.objects.filter(transaction_status='pending')

    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        upi_address = request.POST.get('upi_address')
        # Handle the approval or rejection of the transaction based on the data received

        # Example: Update the transaction status to 'approved' or 'rejected'
        transaction = CustomerBalanceHistory.objects.get(id=transaction_id, upi_address=upi_address)
        
        if request.POST.get('approve'):
            transaction.transaction_status = 'approved'
            transaction.save()
            wallet= CustomerBalance.objects.get(id=transaction.wallet.id)
            wallet.balance = wallet.balance+transaction.amount
            wallet.save()

        elif request.POST.get('reject'):
            transaction.transaction_status = 'rejected'
            transaction.save()

        # Redirect back to the transaction history page
        return redirect('transaction_history')

    context = {'transactions': transactions}
    return render(request, 'kuberaapp/transaction_history.html', context)


def customer_settlements(request):
    accepted_orders = Order.objects.filter(order_status='accepted', draw__released=True)
    context = {'accepted_orders': accepted_orders}
    return render(request, 'kuberaapp/customer_settlements.html', context)

def settle_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    # Perform the settlement logic here, e.g., mark order as settled
    order.order_status = "settled"
    order.save()
    tickets = Ticket.objects.filter(order=order)
    for ticket in tickets:
        ticket.settled=True
        ticket.save()
    return redirect('customer_settlements')


@login_required(login_url='login')
def book_tickets(request,draw_id):
    ticketprices = TicketPrice.objects.all()
    return render(request, 'kuberaapp/book-tickets.html',{"ticketprices":ticketprices,"draw_id":draw_id})


from django.http import JsonResponse

import json
from django.http import JsonResponse

@login_required(login_url='login')
def process_selected_tickets(request,draw_id):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)
           
            selected_ticket_data = request_data  # Assuming the data is a list
            # user = request.user
            draw = Draw.objects.get(id=draw_id)
            order = Order.objects.create(customer=request.user,draw=draw,
                    order_status="pending")
            for i in selected_ticket_data:
                t = TicketPrice.objects.get(id=i["Ticket ID"])
                quantity = int(i["Quantity"])
                number = int(i['Ticket Number'])
                total_amount = t.ticket_value * quantity

                # Create a Ticket instance with calculated values
                ticket = Ticket(
                    # agent=request.user,
                    draw=draw,
                    customer=request.user,
                    board=t,
                    choosen_number=number,
                    quantity=quantity,
                    total_price=total_amount,
                    order=order  # Set the order for the ticket
                )
                
                ticket.save()
                            
                        
            order_total = sum(ticket.total_price for ticket in order.ticket_set.all())
            order.order_total = order_total
            order.save()
            
            
            # Process the selected ticket data here
            # You can loop through the selected_ticket_data list and save it to your database or perform any required actions

            # Return a JSON response
            response_data = {"message": "Selected ticket data processed successfully","order_id":order.id}
            print(response_data)
            return JsonResponse(response_data, status=200)
        except json.JSONDecodeError:
            response_data = {"error": "Invalid JSON data"}
            print(response_data)
            return JsonResponse(response_data, status=400)
    else:
        response_data = {"error": "Invalid request method"}
        print(response_data)
        return JsonResponse(response_data, status=400)


def order_approval_list(request):
    order_approvals = OrderApproval.objects.filter(transaction_status="pending")

    context = {
        'order_approvals': order_approvals
    }

    return render(request, 'kuberaapp/order_approval_list.html', context)

def approve_transaction(request, approval_id):
    approval = OrderApproval.objects.get(pk=approval_id)
    approval.transaction_status = "approved"
    approval.transaction_approved = True
    order= Order.objects.get(id= approval.order.id)
    order.order_status="processing"
    order.save()
    approval.save()
    return redirect('order_approval_list')

def reject_transaction(request, approval_id):
    approval = OrderApproval.objects.get(pk=approval_id)
    approval.transaction_status = "rejected"
    approval.transaction_approved = False
    order= Order.objects.get(id= approval.order.id)
    order.order_status="cancelled"
    order.save()
    approval.save()
    return redirect('order_approval_list')

def ticket_price_list(request):
    ticket_prices = TicketPrice.objects.all()
    context = {'ticket_prices': ticket_prices}
    return render(request, 'kuberaapp/ticket_price.html', context)


from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect(reverse_lazy('home'))