from django.shortcuts import render,redirect,get_object_or_404
from .forms import VoterRegistrationForm, CandidateRegistrationForm, AdminLoginForm
from .models import AdminUser
from .models import Voter, Candidate
from .forms import VoterLoginForm
from django.contrib import messages
from .models import Candidate, Voter, Vote
from django.db.models import Count



# Create your views here.
def home(request):
    return render(request, 'home.html')
def voter_login(request):
    return render(request, 'voter_login.html')

def voter_register(request):
    return render(request, 'voter_register.html')

def admin_login(request):
    return render(request, 'admin_login.html')

def candidate_register(request):
    return render(request, 'candidate_register.html')

def dashboard(request):
    candidates = Candidate.objects.all()
    return render(request, 'dashboard.html', {'candidates': candidates})

def results(request):
    return render(request, 'results.html')



def voter_register(request):
    if request.method == 'POST':
        form = VoterRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Voter registered successfully!')
            return redirect('home')
    else:
        form = VoterRegistrationForm()
    return render(request, 'voter_register.html', {'form': form})

def candidate_register(request):
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate registered successfully!')

            return redirect('home')
    else:
        form = CandidateRegistrationForm()
    return render(request, 'candidate_register.html', {'form': form})

def admin_login(request):
    if request.method == "POST":
        gov_id = request.POST.get('gov_id')
        password = request.POST.get('password')

        try:
            admin = AdminUser.objects.get(gov_id=gov_id, password=password)
            request.session['admin_logged_in'] = True
            request.session['admin_name'] = admin.name
            
            return redirect('admin_dashboard')
        except AdminUser.DoesNotExist:
            messages.error(request, "Invalid Government ID or Password!")

    return render(request, 'admin_login.html')

def voter_login(request):
    if request.method == 'POST':
        voter_card_id = request.POST.get('voter_card_id')
        password = request.POST.get('password')

        # Debugging check
        print("Voter ID entered:", voter_card_id)
        print("Password entered:", password)

        # Make sure both fields are filled
        if not voter_card_id or not password:
            messages.error(request, "Please enter both voter ID and password.")
            return redirect('voter_login')

        try:
            # Use the correct field name from your model
            voter = Voter.objects.get(voter_card_id=voter_card_id, password=password)
            request.session['voter_id'] = voter.id
            messages.success(request, f"Welcome {voter.name}!")
            return redirect('voter_dashboard')
        except Voter.DoesNotExist:
            messages.error(request, "Invalid Voter ID or Password.")
            return redirect('voter_login')

    return render(request, 'voter_login.html')


def vote_page(request):
    voter_id = request.session.get('voter_id')
    if not voter_id:
        return redirect('voter_login')

    voter = Voter.objects.get(id=voter_id)
    candidates = Candidate.objects.filter(constituency=voter.constituency)

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        if not voter.has_voted:
            selected_candidate = Candidate.objects.get(id=candidate_id)
            # You can later add a Vote model, but for now we’ll mark voted.
            voter.has_voted = True
            voter.save()
            messages.success(request, f"You voted for {selected_candidate.name}!")
        else:
            messages.error(request, "You have already voted!")
    return render(request, 'vote_page.html', {'candidates': candidates})


def vote_candidate(request, candidate_id):
    if 'voter_id' not in request.session:
        return redirect('voter_login')

    voter_id = request.session['voter_id']
    voter = Voter.objects.get(id=voter_id)
    candidate = Candidate.objects.get(id=candidate_id)

    # Check if already voted
    if Vote.objects.filter(voter=voter).exists():
        return render(request, 'error.html', {'message': 'You have already voted!'})

    Vote.objects.create(voter=voter, candidate=candidate, constituency=candidate.constituency)
    return render(request, 'success.html', {'message': f'You voted for {candidate.name} successfully!'})

def voter_logout(request):
    request.session.flush()
    messages.success(request, "You have logged out successfully.")
    return redirect('voter_login')

def cast_vote(request, candidate_id):
    if 'voter_id' not in request.session:
        messages.error(request, "You must log in first!")
        return redirect('voter_login')

    voter_id = request.session['voter_id']
    voter = get_object_or_404(Voter, id=voter_id)
    candidate = get_object_or_404(Candidate, id=candidate_id)

    # Check if voter has already voted
    if Vote.objects.filter(voter=voter).exists():
        messages.warning(request, "You have already voted!")
        return redirect('candidate_dashboard')

    # Record the vote
    Vote.objects.create(voter=voter, candidate=candidate, constituency=voter.constituency)
    voter.has_voted = True
    voter.save()

    messages.success(request, f"You have successfully voted for {candidate.name}!")
    return redirect('candidate_dashboard')

def voter_dashboard(request):
    voter_id = request.session.get('voter_id')
    if not voter_id:
        return redirect('voter_login')  # Force login if not logged in

    voter = Voter.objects.get(id=voter_id)
    candidates = Candidate.objects.all()

    return render(request, 'voter_dashboard.html', {
        'voter': voter,
        'candidates': candidates
    })

def view_candidates(request):
    # Fetch all candidates
    candidates = Candidate.objects.all()

    # Pass them to the template
    context = {
        'candidates': candidates
    }
    return render(request, 'view_candidates.html', context)

def admin_dashboard(request):
    if not request.session.get('admin_logged_in'):
        messages.error(request, "Please log in first.")
        return redirect('admin_login')

    # Get selected constituency from dropdown
    selected_constituency = request.GET.get('constituency', '')

    # Get unique list of all constituencies
    constituencies = Candidate.objects.values_list('constituency', flat=True).distinct()

    # Filter candidates based on selected constituency
    if selected_constituency:
        candidates = Candidate.objects.filter(constituency=selected_constituency)
    else:
        candidates = Candidate.objects.all()

    # Prepare candidate vote data
    candidate_data = []
    for candidate in candidates:
        total_votes = Vote.objects.filter(candidate=candidate).count()
        candidate_data.append({
            'name': candidate.name,
            'party_name': candidate.party_name,
            'constituency': candidate.constituency,
            'total_votes': total_votes,
        })

    # Sort by total votes (highest first)
    candidate_data.sort(key=lambda x: x['total_votes'], reverse=True)

    context = {
        'admin_name': request.session.get('admin_name'),
        'candidates': candidate_data,
        'constituencies': constituencies,
        'selected_constituency': selected_constituency,
    }

    return render(request, 'admin_dashboard.html', context)

from django.http import HttpResponse

def election_results(request):
    """
    Simple public results view (no template). Use ?constituency=Name to query.
    Shows ranking, winner details, runner-up and the margin (winner_votes - runner_up_votes).
    Handles ties gracefully.
    """
    constituency = request.GET.get('constituency', '').strip()

    # list available constituencies
    constituencies = Candidate.objects.values_list('constituency', flat=True).distinct()

    if not constituency:
        html = "<h2>Select a constituency to view results:</h2><ul>"
        for c in constituencies:
            if c:
                html += f'<li><a href="?constituency={c}">{c}</a></li>'
        html += "</ul><br><a href='/'>Back to Home</a>"
        return HttpResponse(html)

    # get candidates for the constituency
    candidates_qs = Candidate.objects.filter(constituency__iexact=constituency)
    if not candidates_qs.exists():
        return HttpResponse(f"<h3>No candidates found for '{constituency}'</h3><br><a href='/results/'>Back</a>")

    # build list of (candidate, votes)
    results = []
    for c in candidates_qs:
        votes = Vote.objects.filter(candidate=c).count()
        results.append((c, votes))

    # sort descending by votes
    results.sort(key=lambda x: x[1], reverse=True)

    # compute winner(s)
    winner_votes = results[0][1]
    winners = [r for r in results if r[1] == winner_votes]  # can be multiple in tie

    # determine runner-up votes (second-highest distinct vote count)
    runner_up_votes = 0
    if len(results) > 1:
        # find first vote count < winner_votes
        second_votes = None
        for _, v in results:
            if v < winner_votes:
                second_votes = v
                break
        runner_up_votes = second_votes if second_votes is not None else 0

    # margin = winner_votes - runner_up_votes
    margin = winner_votes - runner_up_votes

    # build html
    html = f"<h1>Election Results for {constituency}</h1>"
    html += "<table border='1' cellpadding='6' style='border-collapse:collapse;'>"
    html += "<tr><th>Rank</th><th>Candidate</th><th>Party</th><th>Votes</th></tr>"

    for idx, (c, v) in enumerate(results, start=1):
        # highlight winners
        row_style = " style='background:#d4edda;'" if v == winner_votes else ""
        html += f"<tr{row_style}><td>{idx}</td><td>{c.name}</td><td>{c.party_name}</td><td>{v}</td></tr>"

    html += "</table><br>"

    if len(winners) > 1:
        # tie
        html += "<h2 style='color:orange;'>Result: Tie</h2>"
        html += "<p>The following candidates are tied for first place:</p><ul>"
        for c, v in winners:
            html += f"<li>{c.name} ({c.party_name}) — {v} votes</li>"
        html += "</ul>"
        html += f"<p><strong>Victory Margin:</strong> 0 votes (tie)</p>"
    else:
        winner = winners[0][0]
        html += f"<h2 style='color:green;'>Winner: {winner.name} ({winner.party_name}) — {winner_votes} votes</h2>"
        if runner_up_votes > 0:
            # normal case with runner-up
            # find runner-up candidate(s) (may be multiple with same runner_up_votes)
            runner_ups = [r for r in results if r[1] == runner_up_votes]
            html += "<p><strong>Runner-up(s):</strong></p><ul>"
            for c, v in runner_ups:
                html += f"<li>{c.name} ({c.party_name}) — {v} votes</li>"
            html += "</ul>"
            html += f"<p><strong>Victory Margin:</strong> {margin} votes (winner_votes - runner_up_votes)</p>"
        else:
            # no runner-up (only one candidate)
            html += "<p>No runner-up (only one candidate). Victory margin is the total votes.</p>"
            html += f"<p><strong>Victory Margin:</strong> {margin} votes</p>"

    # show winner details
    if len(winners) == 1:
        html += "<hr><h3>Winner Details</h3>"
        html += f"<p><strong>Age:</strong> {winner.age}</p>"
        html += f"<p><strong>Qualification:</strong> {winner.qualifications}</p>"
        html += f"<p><strong>Promises:</strong> {winner.promises}</p>"
        if winner.election_symbol:
            try:
                html += f"<div><img src='{winner.election_symbol.url}' style='height:140px; object-fit:contain;'></div>"
            except Exception:
                # media serving might not be configured for this view; ignore image error
                pass

    html += "<br><a href='/results/'>Back to results</a> | <a href='/'>Home</a>"
    return HttpResponse(html)


# def eci_dashboard(request):
#     """
#     Dashboard visible only to logged-in ECI (superuser).
#     Shows voters & candidates overview and details by constituency.
#     """
#     user = request.user
#     if not user.is_superuser:
#         return HttpResponse("<h3>Access denied. Superuser only.</h3>")

#     constituency = request.GET.get("constituency", "").strip()

#     all_constituencies = Candidate.objects.values_list('constituency', flat=True).distinct()

#     html = f"<h1>Welcome, {user.username} (ECI Dashboard)</h1>"
#     html += "<a href='/eci_logout/'>Logout</a><br><br>"

#     # Global counts
#     total_voters = Voter.objects.count()
#     total_candidates = Candidate.objects.count()

#     html += f"<h3>Total Voters: {total_voters}</h3>"
#     html += f"<h3>Total Candidates: {total_candidates}</h3><hr>"

#     # Constituency filter form
#     html += "<form method='GET' action='/eci_dashboard/'>"
#     html += "<label>Select Constituency:</label> "
#     html += "<select name='constituency'>"
#     html += "<option value=''>-- All Constituencies --</option>"
#     for c in all_constituencies:
#         selected = "selected" if c == constituency else ""
#         html += f"<option value='{c}' {selected}>{c}</option>"
#     html += "</select> "
#     html += "<input type='submit' value='View'>"
#     html += "</form><br>"

#     # Filter by constituency if selected
#     if constituency:
#         html += f"<h2>Details for Constituency: {constituency}</h2>"

#         voters = Voter.objects.filter(constituency__iexact=constituency)
#         candidates = Candidate.objects.filter(constituency__iexact=constituency)
#     else:
#         html += "<h2>Showing all constituencies</h2>"
#         voters = Voter.objects.all()
#         candidates = Candidate.objects.all()

#     # Show candidates
#     html += "<h3>Candidates</h3>"
#     if candidates.exists():
#         html += "<table border='1' cellpadding='6' style='border-collapse:collapse;'>"
#         html += "<tr><th>Name</th><th>Party</th><th>Constituency</th><th>Symbol</th></tr>"
#         for c in candidates:
#             symbol = f"<img src='{c.election_symbol.url}' style='height:80px;'>" if c.election_symbol else "N/A"
#             html += f"<tr><td>{c.name}</td><td>{c.party_name}</td><td>{c.constituency}</td><td>{symbol}</td></tr>"
#         html += "</table>"
#     else:
#         html += "<p>No candidates found.</p>"

#     # Show voters
#     html += "<h3>Voters</h3>"
#     if voters.exists():
#         html += "<table border='1' cellpadding='6' style='border-collapse:collapse;'>"
#         html += "<tr><th>Name</th><th>Voter ID</th><th>Constituency</th><th>Email</th></tr>"
#         for v in voters:
#             html += f"<tr><td>{v.name}</td><td>{v.voter_id}</td><td>{v.constituency}</td><td>{v.email}</td></tr>"
#         html += "</table>"
#     else:
#         html += "<p>No voters found.</p>"

#     html += "<br><a href='/'>Home</a>"
#     return HttpResponse(html)


from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Voter, Candidate, Vote

# -------------------------------
# ✅ ECI LOGIN FUNCTION
# -------------------------------
def eci_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("eci_dashboard")
        else:
            return HttpResponse("""
                <h2>Invalid credentials or unauthorized user.</h2>
                <a href="/eci_login/">Try Again</a>
            """)

    # ✅ Simple HTML form (no templates)
    return HttpResponse(f"""
        <h2>ECI Login</h2>
        <form method="post" action="/eci_login/">
            <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
            <label>Username:</label><br>
            <input type="text" name="username" required><br><br>
            <label>Password:</label><br>
            <input type="password" name="password" required><br><br>
            <input type="submit" value="Login">
        </form>
        <br><a href="/">Back to Home</a>
    """)


# -------------------------------
# ✅ ECI DASHBOARD (Superuser only)
# -------------------------------
@login_required
@user_passes_test(lambda u: u.is_superuser)
def eci_dashboard(request):
    # All voters and candidates
    voters = Voter.objects.all()
    candidates = Candidate.objects.all()

    # Constituency-wise summary
    constituency_data = {}

    for constituency in set(voters.values_list('constituency', flat=True)):
        cands = candidates.filter(constituency=constituency)
        votes = Vote.objects.filter(candidate__constituency=constituency)

        # Tally votes for each candidate
        vote_counts = {}
        for cand in cands:
            vote_counts[cand] = votes.filter(candidate=cand).count()

        # Find winner
        if vote_counts:
            sorted_votes = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
            winner, winner_votes = sorted_votes[0]
            margin = 0
            if len(sorted_votes) > 1:
                margin = winner_votes - sorted_votes[1][1]
        else:
            winner = None
            winner_votes = 0
            margin = 0

        constituency_data[constituency] = {
            "total_voters": voters.filter(constituency=constituency).count(),
            "total_candidates": cands.count(),
            "winner": winner,
            "winner_votes": winner_votes,
            "margin": margin,
        }

    # Generate HTML dynamically (no templates)
    html = "<h2>ECI Dashboard</h2>"
    html += "<a href='/'>Back to Home</a><br><br>"
    html += f"<p>Total Voters in System: {voters.count()}</p>"
    html += f"<p>Total Candidates in System: {candidates.count()}</p><hr>"

    for constituency, data in constituency_data.items():
        html += f"<h3>Constituency: {constituency}</h3>"
        html += f"<p>Total Voters: {data['total_voters']}</p>"
        html += f"<p>Total Candidates: {data['total_candidates']}</p>"
        if data['winner']:
            html += f"<p><b>Winner:</b> {data['winner'].name} ({data['winner'].party})</p>"
            html += f"<p>Votes Received: {data['winner_votes']}</p>"
            html += f"<p>Victory Margin: {data['margin']} votes</p>"
        else:
            html += "<p>No votes yet.</p>"
        html += "<hr>"

    return HttpResponse(html)


def eci_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponse("<h3>Access Denied: You must be logged in as ECI Superuser.</h3><a href='/eci_login/'>Login Here</a>")

    selected_constituency = request.GET.get('constituency', '')

    # Get all distinct constituencies
    constituencies = Candidate.objects.values_list('constituency', flat=True).distinct()

    # Filter voters and candidates
    if selected_constituency:
        voters = Voter.objects.filter(constituency=selected_constituency)
        candidates = Candidate.objects.filter(constituency=selected_constituency)
    else:
        voters = Voter.objects.all()
        candidates = Candidate.objects.all()

    # HTML output
    html = f"""
    <h1>ECI Dashboard</h1>
    <form method='get'>
        <label>Select Constituency:</label>
        <select name='constituency'>
            <option value=''>All Constituencies</option>
            {''.join([f"<option value='{c}' {'selected' if c == selected_constituency else ''}>{c}</option>" for c in constituencies])}
        </select>
        <input type='submit' value='Filter'>
    </form>

    <h3>Total Candidates: {candidates.count()}</h3>
    <ul>
    """
    for c in candidates:
        html += f"<li><b>{c.name}</b> - {c.party_name} ({c.constituency})</li>"
    html += "</ul>"

    html += f"<h3>Total Voters: {voters.count()}</h3><ul>"
    for v in voters:
        html += f"<li><b>{v.name}</b> - {v.constituency}</li>"
    html += "</ul>"

    html += "<br><a href='/'>Back to Home</a>"

    return HttpResponse(html)