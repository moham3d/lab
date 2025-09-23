import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"
import bcrypt from "bcryptjs"

export async function POST(request: NextRequest) {
  try {
    const { username, password } = await request.json()

    if (!username || !password) {
      return NextResponse.json(
        { detail: "Username and password are required" },
        { status: 400 }
      )
    }

    // Find user by username
    const user = await db.user.findUnique({
      where: { username },
    })

    if (!user || !user.isActive) {
      return NextResponse.json(
        { detail: "Invalid credentials" },
        { status: 401 }
      )
    }

    // Verify password (in production, use proper password hashing)
    const isPasswordValid = await bcrypt.compare(password, user.password || "")
    
    if (!isPasswordValid) {
      return NextResponse.json(
        { detail: "Invalid credentials" },
        { status: 401 }
      )
    }

    // Update last login
    await db.user.update({
      where: { id: user.id },
      data: { lastLogin: new Date() },
    })

    // Create JWT token (simplified for demo)
    const token = Buffer.from(`${user.id}:${user.role}`).toString('base64')

    return NextResponse.json({
      access_token: token,
      token_type: "bearer",
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        fullName: user.fullName,
        role: user.role,
        isActive: user.isActive,
      },
    })
  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}