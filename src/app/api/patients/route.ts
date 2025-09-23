import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { ssn, mobileNumber, fullName, dateOfBirth, gender, address } = body

    // Validate required fields
    if (!ssn || !mobileNumber || !fullName || !dateOfBirth || !gender) {
      return NextResponse.json(
        { detail: "Missing required fields" },
        { status: 400 }
      )
    }

    // Validate SSN format (14 digits)
    if (!/^\d{14}$/.test(ssn)) {
      return NextResponse.json(
        { detail: "SSN must be exactly 14 digits" },
        { status: 400 }
      )
    }

    // Validate mobile number format (Egyptian format)
    if (!/^01\d{9}$/.test(mobileNumber)) {
      return NextResponse.json(
        { detail: "Mobile number must start with 01 followed by 9 digits" },
        { status: 400 }
      )
    }

    // Check if patient already exists
    const existingPatient = await db.patient.findUnique({
      where: { ssn },
    })

    if (existingPatient) {
      return NextResponse.json(
        { detail: "Patient with this SSN already exists" },
        { status: 400 }
      )
    }

    // Create patient
    const patient = await db.patient.create({
      data: {
        ssn,
        mobileNumber,
        fullName,
        dateOfBirth: new Date(dateOfBirth),
        gender,
        address: address || null,
      },
    })

    return NextResponse.json(patient, { status: 201 })
  } catch (error) {
    console.error("Error creating patient:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}