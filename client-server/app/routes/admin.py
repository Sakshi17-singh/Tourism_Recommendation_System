from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import SessionLocal
from ..models import Admin, Booking, Review
import requests
import os
from datetime import datetime
import json

# -----------------------------
# Blueprint
# -----------------------------
admin_bp = Blueprint("admin", __name__)

# -----------------------------
# Admin Login
# -----------------------------
@admin_bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400

    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    db: Session = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.username == username).first()
        if not admin or admin.password != password:
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({
            "message": "Admin login successful",
            "admin_id": admin.id,
            "username": admin.username
        }), 200
    finally:
        db.close()

# -----------------------------
# Clerk Helper
# -----------------------------
CLERK_API_KEY = os.environ.get("CLERK_API_KEY")
CLERK_API_URL = "https://api.clerk.dev/v1/users"

def get_users_from_clerk():
    if not CLERK_API_KEY:
        print("⚠️ CLERK_API_KEY is missing!")
        return []

    headers = {"Authorization": f"Bearer {CLERK_API_KEY}"}
    try:
        response = requests.get(CLERK_API_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print("⚠️ Clerk API error:", response.status_code, response.text)
            return []
    except Exception as e:
        print("⚠️ Clerk API request failed:", str(e))
        return []

# -----------------------------
# Dashboard Endpoints
# -----------------------------

# Total registered users
@admin_bp.route("/admin/dashboard/user-count", methods=["GET"])
def total_users():
    users = get_users_from_clerk()
    valid_users = [u for u in users if u.get("id")]
    return jsonify({"totalUsers": len(valid_users)})

# New users this month
@admin_bp.route("/admin/dashboard/new-users", methods=["GET"])
def new_users():
    users = get_users_from_clerk()
    this_month = datetime.utcnow().month
    count = 0

    for u in users:
        created_at = u.get("created_at")
        if not created_at:
            continue
        try:
            if isinstance(created_at, int):
                if created_at > 1e12:  # milliseconds
                    created_at /= 1000
                dt = datetime.utcfromtimestamp(created_at)
            else:
                dt = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))

            if dt.month == this_month:
                count += 1
        except Exception:
            continue

    return jsonify({"newUsersThisMonth": count})

# Total bookings from SQLite
@admin_bp.route("/admin/dashboard/total-bookings", methods=["GET"])
def total_bookings():
    session = SessionLocal()
    count = session.query(Booking).count()
    session.close()
    return jsonify({"totalBookings": count})

# Bookings per city
@admin_bp.route("/admin/dashboard/bookings-per-city", methods=["GET"])
def bookings_per_city():
    session = SessionLocal()
    results = session.query(Booking.city, func.count(Booking.id)).group_by(Booking.city).all()
    session.close()
    data = [{"city": row[0], "count": row[1]} for row in results]
    return jsonify(data)


# -----------------------------
# Review Management Endpoints
# -----------------------------

# Get all reviews for admin panel
@admin_bp.route("/admin/reviews", methods=["GET"])
def admin_get_reviews():
    """Get all reviews with filtering options"""
    try:
        session = SessionLocal()
        
        # Get query parameters
        status = request.args.get("status")  # pending, approved, rejected, all
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        
        # Build query
        query = session.query(Review)
        
        if status and status != "all":
            query = query.filter(Review.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        reviews = query.order_by(Review.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        # Format response
        reviews_list = []
        for review in reviews:
            reviews_list.append({
                "id": review.id,
                "name": review.name,
                "email": review.email,
                "place": review.place,
                "visit_date": review.visit_date,
                "type": review.type,
                "rating": review.rating,
                "review": review.review,
                "recommend": review.recommend,
                "images": json.loads(review.images) if review.images else [],
                "status": review.status,
                "created_at": review.created_at.isoformat() if review.created_at else None,
                "approved_at": review.approved_at.isoformat() if review.approved_at else None,
                "admin_notes": review.admin_notes
            })
        
        return jsonify({
            "reviews": reviews_list,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        print(f"Error fetching reviews: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Get review statistics for dashboard
@admin_bp.route("/admin/dashboard/review-stats", methods=["GET"])
def review_stats():
    """Get review statistics for admin dashboard"""
    try:
        session = SessionLocal()
        
        total_reviews = session.query(Review).count()
        pending_reviews = session.query(Review).filter(Review.status == "pending").count()
        approved_reviews = session.query(Review).filter(Review.status == "approved").count()
        rejected_reviews = session.query(Review).filter(Review.status == "rejected").count()
        
        # Average rating of approved reviews
        avg_rating = session.query(func.avg(Review.rating)).filter(Review.status == "approved").scalar()
        
        # Recent reviews (last 5)
        recent_reviews = session.query(Review).order_by(Review.created_at.desc()).limit(5).all()
        recent_list = []
        for review in recent_reviews:
            recent_list.append({
                "id": review.id,
                "name": review.name,
                "place": review.place,
                "rating": review.rating,
                "status": review.status,
                "created_at": review.created_at.isoformat() if review.created_at else None
            })
        
        return jsonify({
            "total_reviews": total_reviews,
            "pending_reviews": pending_reviews,
            "approved_reviews": approved_reviews,
            "rejected_reviews": rejected_reviews,
            "average_rating": round(avg_rating, 2) if avg_rating else 0,
            "recent_reviews": recent_list
        }), 200
        
    except Exception as e:
        print(f"Error fetching review stats: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Approve review
@admin_bp.route("/admin/reviews/<int:review_id>/approve", methods=["POST"])
def approve_review(review_id):
    """Approve a review"""
    try:
        session = SessionLocal()
        review = session.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        data = request.get_json() or {}
        admin_notes = data.get("admin_notes")
        
        review.status = "approved"
        review.approved_at = datetime.utcnow()
        if admin_notes:
            review.admin_notes = admin_notes
        
        session.commit()
        
        return jsonify({
            "message": "Review approved successfully",
            "review_id": review.id
        }), 200
        
    except Exception as e:
        print(f"Error approving review: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Reject review
@admin_bp.route("/admin/reviews/<int:review_id>/reject", methods=["POST"])
def reject_review(review_id):
    """Reject a review"""
    try:
        session = SessionLocal()
        review = session.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        data = request.get_json() or {}
        admin_notes = data.get("admin_notes")
        
        review.status = "rejected"
        if admin_notes:
            review.admin_notes = admin_notes
        
        session.commit()
        
        return jsonify({
            "message": "Review rejected successfully",
            "review_id": review.id
        }), 200
        
    except Exception as e:
        print(f"Error rejecting review: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Delete review
@admin_bp.route("/admin/reviews/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    """Delete a review"""
    try:
        session = SessionLocal()
        review = session.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        # Delete associated images
        if review.images:
            image_paths = json.loads(review.images)
            for image_path in image_paths:
                full_path = os.path.join(os.getcwd(), image_path.lstrip('/'))
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        print(f"Error deleting image {full_path}: {str(e)}")
        
        session.delete(review)
        session.commit()
        
        return jsonify({"message": "Review deleted successfully"}), 200
        
    except Exception as e:
        print(f"Error deleting review: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
